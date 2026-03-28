# Trading System - Schnellstart

**Geschätzte Zeit:** 15 Minuten  
**Schwierigkeitsgrad:** Anfänger  

## Schritt 1: Archiv entpacken

Sie haben das Archiv bereits entpackt! 

## Schritt 2: Umgebungsvariablen konfigurieren

```bash
# Konfigurationsdatei erstellen
cp .env.example .env

# Bearbeiten Sie die .env-Datei
nano .env  # oder verwenden Sie Ihren bevorzugten Editor
```

**Mindestanforderungen in .env:**
```bash
TRADING_MASTER_PASSWORD=IhrSicheresPasswortHier123!
WEBHOOK_SECRET=IhrWebhookSecretHier456!
```

## Schritt 3: Wählen Sie Ihre Installationsmethode

### Option A: Docker (Empfohlen - Einfachste Installation)

```bash
# System starten
docker-compose up -d

# Status überprüfen
docker-compose ps

# Dashboard öffnen
open http://localhost:3000
```

**Das war's! Ihr System läuft jetzt.**

### Option B: Lokale Installation

#### Backend starten:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# oder: venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main_simple.py
```

#### Frontend starten (neues Terminal):
```bash
cd frontend
npm install
npm run dev
```

**Dashboard öffnen:** http://localhost:5174

## Schritt 4: System testen

### API-Test:
```bash
curl http://localhost:5001/api/health
```

**Erwartete Antwort:**
```json
{
  "status": "healthy",
  "service": "Trading System API"
}
```

### Dashboard-Test:
1. Öffnen Sie das Dashboard im Browser
2. Gehen Sie zum "Overview" Tab
3. Alle Komponenten sollten "Online" anzeigen

## Schritt 5: Erste Trading-Tests

### Signal abrufen:
```bash
curl http://localhost:5001/api/signals/recommendations
```

### Test-Order erstellen (Paper Trading):
```bash
curl -X POST http://localhost:5001/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.01,
    "order_type": "MARKET"
  }'
```

## Herzlichen Glückwunsch!

Ihr Trading-System ist jetzt einsatzbereit!

## Nächste Schritte

### Für Einsteiger:
1. **Erkunden Sie das Dashboard** - Alle 6 Tabs durchgehen
2. **Paper Trading testen** - Risikofreie Trades ausführen
3. **Dokumentation lesen** - `docs/TRADING_SYSTEM_DOCUMENTATION.md`

### Für Fortgeschrittene:
1. **API-Schlüssel konfigurieren** - Für Live-Daten
2. **TradingView-Webhooks einrichten** - Externe Signale
3. **Broker-Integration** - Für Live-Trading

### Für Entwickler:
1. **Code erkunden** - `backend/` und `frontend/` Verzeichnisse
2. **Tests ausführen** - `python test_suite.py`
3. **API-Referenz** - `docs/API_REFERENCE.md`

## ️ Wichtige Sicherheitshinweise

1. **Starten Sie mit Paper Trading** - Niemals sofort Live-Trading!
2. **Starke Passwörter verwenden** - Ändern Sie alle Defaults
3. **System überwachen** - Nutzen Sie das Dashboard
4. **Backups erstellen** - Automatisch konfiguriert
5. **Dokumentation lesen** - Besonders Sicherheitsabschnitt

## 🆘 Probleme?

### Häufige Lösungen:
- **Port bereits belegt:** Ändern Sie Ports in der Konfiguration
- **Python-Fehler:** Virtuelle Umgebung aktivieren
- **Docker-Probleme:** `docker-compose down && docker-compose up -d`
- **API-Fehler:** Überprüfen Sie .env-Datei

### Hilfe finden:
- **Vollständige Dokumentation:** `docs/TRADING_SYSTEM_DOCUMENTATION.md`
- **API-Referenz:** `docs/API_REFERENCE.md`
- **Troubleshooting:** Dokumentation Abschnitt 10

---

** Viel Erfolg mit Ihrem automatisierten Trading-System!**

