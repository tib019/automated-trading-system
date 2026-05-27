# ADR-002: Flask + synchrones Python statt FastAPI/async

**Status:** Accepted  
**Datum:** 2024

## Kontext

Das Backend benötigt einen HTTP-Server für das React-Dashboard und Webhook-Endpoints. In Python gibt es zwei dominante Web-Frameworks:

- **Flask:** WSGI (synchron), weit verbreitet, simples Request/Response-Modell
- **FastAPI:** ASGI (async), modernes Python, automatische OpenAPI-Docs, Pydantic-Validierung

## Entscheidung

Wir verwenden **Flask 2.3 mit synchronem Python**.

Der Kerngrund: Die Daten-Pipeline (Data Collector → Sentiment Analyzer → Signal Generator) ist **CPU-gebunden** und arbeitet mit Pandas DataFrames, NumPy-Arrays und scikit-learn-Modellen. Diese Operationen sind von Natur aus synchron und blockierend.

Async wäre nur dann ein Gewinn, wenn der Bottleneck in I/O-Wartezeiten liegt (Netzwerk, Disk). Da der Bottleneck hier CPU ist (NLP-Berechnung), würde `async/await` nur Komplexität hinzufügen ohne Durchsatzgewinn.

```python
# signal_generator.py — typischer synchroner Aufruf
def generate_signals(symbol: str) -> dict:
    raw_data = collector.fetch(symbol)          # I/O — relativ schnell
    sentiment = analyzer.analyze(raw_data)      # CPU — Hauptarbeit
    signals = model.predict(sentiment.features) # CPU — ML-Inference
    return signals
```

## Abgewogene Alternativen

**FastAPI:** Wäre die bessere Wahl für ein API-first-System mit vielen concurrent Clients. Für dieses Projekt mit einem einzelnen Dashboard-Client und CPU-bound Backend kein Vorteil.

**Celery + Flask:** Für echten Async-Support in der Pipeline wäre Celery (Task Queue) die saubere Lösung. Würde den Scope erheblich vergrößern und wurde als zukünftige Erweiterung notiert.

## Konsequenzen

**Positiv:**
- Synchroner Code ist einfacher zu debuggen und zu testen
- Flask + SQLAlchemy ist eine gut dokumentierte, stabile Kombination
- Kein `asyncio`-Event-Loop zwischen Pandas-Operationen

**Negativ:**
- Keine nativen WebSocket-Fähigkeiten (wird über `flask-socketio` gelöst)
- Skaliert nicht horizontal für viele concurrent API-Clients
- Blocking Calls im Hauptthread könnten Dashboard-Responsiveness beeinträchtigen bei langen Berechnungen
