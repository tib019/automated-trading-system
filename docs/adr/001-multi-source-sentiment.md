# ADR-001: Multi-Source Sentiment als primäre Signalstrategie

**Status:** Accepted  
**Datum:** 2024

## Kontext

Das System braucht eine primäre Datenquelle für Trading-Signale. Die klassischen Alternativen sind:

- **Technische Analyse** (Preis-Charts, Indikatoren wie RSI, MACD, Bollinger Bands)
- **Fundamentalanalyse** (Unternehmenskennzahlen, Earnings, Wirtschaftsdaten)
- **Sentiment-Analyse** (öffentliche Meinungen aus Social Media und News)

## Entscheidung

Wir verwenden **Sentiment-Analyse aus drei parallelen Quellen**: Twitter (Tweepy), Reddit (PRAW) und Yahoo Finance News (yfinance).

Die These: Stimmungsveränderungen in sozialen Medien führen Preisbewegungen voraus, besonders in liquiden Crypto-Märkten (BTC, ETH). Durch die Kombination dreier Quellen werden Ausreißer und Manipulation einzelner Plattformen abgefedert.

```python
# sentiment_analyzer.py — Aggregation der Quellen
scores = {
    'twitter': analyze_twitter(symbol),   # Kurzfristige Stimmung
    'reddit':  analyze_reddit(symbol),    # Community-Konsens
    'news':    analyze_news(symbol),      # Nachrichtenkontext
}
composite_score = weighted_average(scores, weights=[0.4, 0.35, 0.25])
```

## Abgewogene Alternativen

**Nur technische Analyse:** Einfacher umzusetzen, keine API-Abhängigkeiten. Aber technische Signale sind lagging indicators — sie reagieren auf Preisbewegungen, antizipieren sie nicht.

**Hybridmodell (Sentiment + TA):** Wäre die robustere Lösung für ein Produktionssystem. Wurde bewusst aus Scope ausgeschlossen, um den ML-Anteil isoliert validieren zu können.

## Konsequenzen

**Positiv:**
- Drei unabhängige Quellen reduzieren False-Positive-Rate
- Frühzeitige Signale bei viralen Ereignissen (Elon Musk-Tweets etc.)
- Lernziel: NLP-Pipeline end-to-end implementieren

**Negativ:**
- Drei API-Abhängigkeiten mit Rate-Limits und möglichen Zugriffsänderungen (Twitter API wurde 2023 kostenpflichtig)
- Sentiment-Signale sind laut und rauschreich; Noise-Filterung ist aufwändig
- Modell-Bias durch Datenlage: Social Media überrepräsentiert Retail-Investoren
