# Datenquellen für die Analyse

Übersicht möglicher Quellen für Markt- und Sentiment-/Alternativdaten — mit und
ohne API-Anbindung. Alle laufen über `backend/data_api.py` (`ApiClient.call_api`),
fehlertolerant: fällt eine Quelle aus, degradiert die Pipeline sauber.

## Ohne API-Key (frei nutzbar)

| Quelle | Was | Endpoint in `data_api` | Status |
|--------|-----|------------------------|--------|
| **Yahoo Finance** | OHLCV-Kurse, intraday + historisch | `YahooFinance/get_stock_chart` | wired |
| **Stooq** | Tägliche OHLC (CSV) — Markt-Fallback bei Yahoo-Limits | `Stooq/daily` | verfügbar |
| **Reddit** (öffentl. JSON) | Posts aus Subreddits → Sentiment | `Reddit/AccessAPI` | wired |
| **StockTwits** | Finanz-native Nachrichten mit Bullish/Bearish-Label | `StockTwits/symbol_stream` | verfügbar |
| **Fear & Greed (Krypto)** | Marktregime-Index 0–100 (alternative.me) | `FearGreed/crypto` | verfügbar |

### Weitere frei/keyless denkbare Quellen (noch nicht angebunden)
- **Google Trends** (`pytrends`) — Suchinteresse als Aufmerksamkeits-Proxy.
- **Wikipedia Pageviews API** — Aufmerksamkeit für Firmen/Assets.
- **SEC EDGAR** (`data.sec.gov`) — Filings/Events (8-K, 10-Q), Insidergeschäfte.
- **CoinGecko** — Krypto-Preise, Marktkapitalisierung, Volumen (ohne Key).
- **RSS-News** (Yahoo Finance / Google News RSS) — Schlagzeilen für News-Sentiment.
- **CNN Fear & Greed (Aktien)** — Marktregime für Aktien.
- **On-Chain-Daten** (Blockchain-Explorer) — Krypto-Flows, aktive Adressen.
- **FRED** (Makrodaten, freier Key) — Zinsen, Inflation, Arbeitsmarkt als Kontext.

## Mit API-Key (bessere Abdeckung/Latenz)

| Quelle | Was | Key |
|--------|-----|-----|
| **Twitter/X API v2** | Echtzeit-Tweets → Sentiment | `TWITTER_BEARER_TOKEN` (wired) |
| **Finnhub** | Kurse, News, News-Sentiment, Fundamentaldaten | frei/bezahlt |
| **Alpha Vantage** | Kurse, technische Indikatoren, News-Sentiment | frei |
| **Polygon.io** | Tick/Aggregate-Kurse, News | bezahlt |
| **Twelve Data** | Kurse, Indikatoren | frei/bezahlt |
| **NewsAPI / Marketaux** | Nachrichten-Aggregation + Sentiment | frei/bezahlt |
| **Binance / IBKR** | Live-Kurse & Order-Ausführung (Broker) | Konto-Keys |

Keys gehören in die `.env` (siehe `.env.example`) und werden **nie** committet.

## Integration eines neuen Sentiment-Signals (Muster)

1. Neue Methode in `data_api.py` (`_meinquelle`) + Dispatch in `call_api`,
   fehlertolerant, mit `_empty_for`-Fallback.
2. Collector, der die Quelle abruft, Symbole extrahiert, Text mit
   `AdvancedSentimentAnalyzer` bewertet und in die `sentiment_data`-Tabelle
   schreibt (Muster: `RedditCollector` in `data_collector.py`).
3. `SentimentAggregator` fusioniert automatisch alle Quellen nach Zeitfenster,
   Engagement und Quelle — der Signalpfad muss nicht angefasst werden.

## Warum mehrere Quellen?

Mehr **unkorrelierte** Signalquellen senken das Risiko von Fehlsignalen
(Ensemble-Effekt) — analog zur Diversifikation im Portfolio: Der
Diversifikations-/Kovarianz-Ansatz im Risiko-Modul (`risk_analytics.py`) gilt
sinngemäß auch für Datensignale. Einzelne Quellen (v.a. Social Media) sind
manipulierbar; die Aggregation über mehrere Quellen macht das Signal robuster.
