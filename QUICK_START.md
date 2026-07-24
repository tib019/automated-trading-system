# Trading System - Schnellstart

**Geschätzte Zeit:** ~5 Minuten
**Standardmodus:** PAPER_TRADING (kein echtes Geld, keine API-Keys nötig)

## Option A: Docker (empfohlen)

Das System läuft sofort out-of-the-box im Paper-Trading-Modus – eine `.env` ist
optional.

```bash
# Stack bauen und starten
docker compose up -d --build

# Status prüfen (beide Container sollten "healthy" werden)
docker compose ps

# Dashboard öffnen
open http://localhost:3000     # bzw. im Browser aufrufen
```

Das Dashboard (Port 3000) spricht über einen nginx-Proxy mit der Trading-API
(Port 5001). Fertig.

**Stoppen / neu starten:**
```bash
docker compose down
docker compose up -d --build
```

### Optional: eigene Secrets

Nur nötig für Live-Daten/Live-Trading – für Paper Trading überspringen:

```bash
cp .env.example .env
# .env bearbeiten (Broker-Keys, Webhook-Secret, ...)
```

Die `.env` wird automatisch geladen, wenn sie existiert.

## Option B: Lokale Installation (Entwicklung)

**Backend (Terminal 1):**
```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/webhook_server.py    # läuft auf Port 5001
```

**Frontend (Terminal 2):**
```bash
cd frontend
corepack enable                     # aktiviert pnpm
pnpm install
pnpm dev                            # Vite-Dev-Server, siehe Ausgabe (i.d.R. http://localhost:5173)
```

Der Vite-Dev-Server proxied `/api` automatisch an das Backend auf Port 5001.

## System testen

**Health-Check (direkt am Backend):**
```bash
curl http://localhost:5001/health
```
Erwartet: `{"status": "healthy", "service": "TradingView Webhook Server", ...}`

**Über das Dashboard (nginx-Proxy):**
```bash
curl http://localhost:3000/api/status
curl http://localhost:3000/api/brokers
```

**Paper-Test-Order auslösen:**
```bash
curl -X POST http://localhost:3000/api/webhook/test \
  -H "Content-Type: application/json" -d '{}'
```
Erwartet: eine gefüllte Paper-Order (`"broker": "PAPER_TRADING"`).

## Tests ausführen

```bash
pip install -r requirements.txt
pytest -q          # Unit-/Funktions-/Regressionstests (aus dem Repo-Root)
```

## Wichtige Sicherheitshinweise

1. **Immer mit Paper Trading starten** – das ist der Default. Live-Trading erst
   nach ausgiebigem Test bewusst aktivieren.
2. **Keine Secrets committen** – `.env`, Keys und Datenbanken sind in
   `.gitignore` ausgeschlossen.
3. Automatisiertes Trading auf Basis von Social-Media-Sentiment ist mit echtem
   Kapital riskant. Erst verstehen, dann Geld einsetzen.

## Ports auf einen Blick

| Dienst              | Port |
|---------------------|------|
| Dashboard (nginx)   | 3000 |
| Trading-API         | 5001 |
| Vite-Dev-Server     | 5173 |

## Probleme?

- **Port belegt:** anderen Prozess beenden oder Ports in `docker-compose.yml`
  anpassen.
- **Docker neu aufsetzen:** `docker compose down && docker compose up -d --build`
- **Weitere Doku:** `docs/`
