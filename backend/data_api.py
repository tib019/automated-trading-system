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

    @staticmethod
    def _empty_for(endpoint: str) -> dict:
        if endpoint == "YahooFinance/get_stock_chart":
            return {"chart": {"result": []}}
        if endpoint == "Reddit/AccessAPI":
            return {"posts": []}
        if endpoint == "Twitter/search_twitter":
            return {"tweets": []}
        return {}
