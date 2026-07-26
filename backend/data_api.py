"""
data_api - lightweight data client for the trading pipeline.

The original build environment provided a proprietary ``ApiClient`` whose
``call_api`` method proxied a handful of hosted data endpoints. That module was
never part of the repository, so every collector importing it failed.

This is a real, self-contained replacement backed by public data sources:

    * ``YahooFinance/get_stock_chart`` -> Yahoo's public chart API (no key)
    * ``Reddit/AccessAPI``            -> Reddit's public listing JSON (no key)
    * ``Twitter/search_twitter``      -> Twitter/X API v2 if TWITTER_BEARER_TOKEN
                                         is set, otherwise an empty result

Every call is defensive: on any network/parse error it returns an empty result
in the shape the callers expect, so the pipeline degrades gracefully instead of
crashing when a source is unreachable or unauthenticated.
"""

import os
import logging

import requests

logger = logging.getLogger(__name__)

# Yahoo rejects requests without a browser-like User-Agent.
_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
_TIMEOUT = 15


class ApiClient:
    """Drop-in data client. Dispatches ``call_api`` by endpoint name."""

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.session.headers.update({"User-Agent": _UA})
        self._yahoo_primed = False

    def _prime_yahoo(self):
        """Yahoo increasingly rate-limits (429) requests that arrive without a
        session cookie. A single hit to the landing page establishes one."""
        if self._yahoo_primed:
            return
        try:
            self.session.get("https://finance.yahoo.com/", timeout=_TIMEOUT)
        except Exception as exc:
            logger.debug("Yahoo cookie priming failed: %s", exc)
        self._yahoo_primed = True

    def call_api(self, endpoint: str, query: dict | None = None) -> dict:
        query = query or {}
        try:
            if endpoint == "YahooFinance/get_stock_chart":
                return self._yahoo_chart(query)
            if endpoint == "Reddit/AccessAPI":
                return self._reddit(query)
            if endpoint == "Twitter/search_twitter":
                return self._twitter(query)
            if endpoint == "StockTwits/symbol_stream":
                return self._stocktwits(query)
            if endpoint == "Stooq/daily":
                return self._stooq(query)
            if endpoint == "FearGreed/crypto":
                return self._fear_greed(query)
        except Exception as exc:  # never let a data source take down the pipeline
            logger.warning("data_api call to %s failed: %s", endpoint, exc)
        return self._empty_for(endpoint)

    # --- endpoints -----------------------------------------------------------

    def _yahoo_chart(self, query: dict) -> dict:
        symbol = query.get("symbol", "")
        params = {
            "region": query.get("region", "US"),
            "interval": query.get("interval", "1h"),
            "range": query.get("range", "1d"),
            "includeAdjustedClose": str(query.get("includeAdjustedClose", True)).lower(),
        }
        self._prime_yahoo()
        # query2 is the more permissive host; fall back to query1.
        last_exc = None
        for host in ("query2", "query1"):
            url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{symbol}"
            try:
                resp = self.session.get(url, params=params, timeout=_TIMEOUT)
                if resp.status_code == 429:
                    last_exc = requests.HTTPError("429 Too Many Requests")
                    continue
                resp.raise_for_status()
                # Yahoo already returns {'chart': {'result': [...]}} - the exact
                # shape the collectors parse - so pass it straight through.
                return resp.json()
            except requests.RequestException as exc:
                last_exc = exc
        if last_exc:
            raise last_exc
        return {"chart": {"result": []}}

    def _reddit(self, query: dict) -> dict:
        subreddit = query.get("subreddit", "")
        limit = query.get("limit", "25")
        url = f"https://www.reddit.com/r/{subreddit}/new.json"
        resp = self.session.get(url, params={"limit": limit}, timeout=_TIMEOUT)
        resp.raise_for_status()
        children = resp.json().get("data", {}).get("children", [])
        # Callers expect {'posts': [{'data': {...}}, ...]}; Reddit's children
        # are already {'kind': ..., 'data': {...}}.
        return {"posts": [{"data": c.get("data", {})} for c in children]}

    def _twitter(self, query: dict) -> dict:
        bearer = os.environ.get("TWITTER_BEARER_TOKEN")
        if not bearer:
            # X/Twitter search requires an authenticated (paid) API. Without a
            # token we return no tweets rather than pretending.
            return {"tweets": []}
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": query.get("query", ""),
            "max_results": query.get("max_results", 10),
            "tweet.fields": "public_metrics,created_at",
            "expansions": "author_id",
            "user.fields": "username",
        }
        headers = {"Authorization": f"Bearer {bearer}"}
        resp = self.session.get(url, params=params, headers=headers, timeout=_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
        users = {
            u["id"]: u for u in payload.get("includes", {}).get("users", [])
        }
        tweets = []
        for t in payload.get("data", []):
            user = users.get(t.get("author_id"), {})
            tweets.append(
                {
                    "text": t.get("text", ""),
                    "user": {"username": user.get("username", "")},
                    "public_metrics": t.get("public_metrics", {}),
                }
            )
        return {"tweets": tweets}

    def _stocktwits(self, query: dict) -> dict:
        """StockTwits symbol stream - a free, finance-native sentiment source.

        Many messages carry an explicit Bullish/Bearish label; unlabeled ones
        fall back to text sentiment downstream. Returns
        {'messages': [{'body': str, 'sentiment': 'Bullish'|'Bearish'|None,
        'user': str, 'likes': int}]}.
        """
        symbol = query.get("symbol", "")
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        resp = self.session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        out = []
        for m in resp.json().get("messages", []):
            ent = (m.get("entities") or {}).get("sentiment") or {}
            out.append({
                "body": m.get("body", ""),
                "sentiment": ent.get("basic"),  # 'Bullish' / 'Bearish' / None
                "user": (m.get("user") or {}).get("username", ""),
                "likes": (m.get("likes") or {}).get("total", 0),
            })
        return {"messages": out}

    def _stooq(self, query: dict) -> dict:
        """Stooq daily OHLC as a keyless market-data fallback when Yahoo is
        unavailable. Returns {'candles': [{'date','open','high','low','close',
        'volume'}]}. Stooq tickers usually need a suffix (e.g. 'aapl.us')."""
        symbol = query.get("symbol", "").lower()
        url = f"https://stooq.com/q/d/l/?s={symbol}&i={query.get('interval', 'd')}"
        resp = self.session.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        candles = []
        for line in lines[1:]:  # skip header
            parts = line.split(",")
            if len(parts) >= 6 and parts[1] not in ("", "N/D"):
                try:
                    candles.append({
                        "date": parts[0], "open": float(parts[1]),
                        "high": float(parts[2]), "low": float(parts[3]),
                        "close": float(parts[4]), "volume": float(parts[5]),
                    })
                except ValueError:
                    continue
        return {"candles": candles}

    def _fear_greed(self, query: dict) -> dict:
        """Crypto Fear & Greed index (alternative.me) - a market-regime gauge,
        no key. Returns {'value': int 0-100, 'classification': str}."""
        limit = query.get("limit", 1)
        resp = self.session.get(f"https://api.alternative.me/fng/?limit={limit}", timeout=_TIMEOUT)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            return {"value": None, "classification": None}
        latest = data[0]
        return {
            "value": int(latest.get("value", 0)),
            "classification": latest.get("value_classification"),
            "history": data,
        }

    @staticmethod
    def _empty_for(endpoint: str) -> dict:
        if endpoint == "YahooFinance/get_stock_chart":
            return {"chart": {"result": []}}
        if endpoint == "Reddit/AccessAPI":
            return {"posts": []}
        if endpoint == "Twitter/search_twitter":
            return {"tweets": []}
        if endpoint == "StockTwits/symbol_stream":
            return {"messages": []}
        if endpoint == "Stooq/daily":
            return {"candles": []}
        if endpoint == "FearGreed/crypto":
            return {"value": None, "classification": None}
        return {}
