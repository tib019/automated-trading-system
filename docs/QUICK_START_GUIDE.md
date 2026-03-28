# Trading System - Schnellstart-Anleitung

**Geschätzte Zeit:** 15 Minuten  
**Schwierigkeitsgrad:** Anfänger bis Fortgeschritten  

## Überblick

Diese Schnellstart-Anleitung führt Sie durch die grundlegende Installation und Konfiguration des Trading-Systems. Nach Abschluss dieser Anleitung haben Sie ein funktionsfähiges Trading-System, das bereit für Paper Trading ist.

## Voraussetzungen

- **Python 3.11+** installiert
- **Git** für Repository-Verwaltung
- **4 GB RAM** minimum (8 GB empfohlen)
- **Internetverbindung** für API-Zugriff
- **Terminal/Kommandozeile** Grundkenntnisse

## Schritt 1: System herunterladen

```bash
# Arbeitsverzeichnis erstellen
mkdir trading_system_workspace
cd trading_system_workspace

# Repository klonen (oder Dateien kopieren)
git clone <repository_url> .
# oder
# Dateien aus dem bereitgestellten Archiv extrahieren
```

## Schritt 2: Python-Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python3.11 -m venv trading_env

# Virtuelle Umgebung aktivieren
# Linux/macOS:
source trading_env/bin/activate
# Windows:
# trading_env\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Schritt 3: Grundkonfiguration

```bash
# Konfigurationsdatei erstellen
cp .env.example .env

# Konfiguration bearbeiten (verwenden Sie Ihren bevorzugten Editor)
nano .env
```

**Minimale .env-Konfiguration:**
```bash
TRADING_MASTER_PASSWORD=your_secure_password_here
WEBHOOK_SECRET=your_webhook_secret_here
OPENAI_API_KEY=optional_openai_key
```

## Schritt 4: Datenbank initialisieren

```bash
cd trading_system
python init_database.py
```

**Erwartete Ausgabe:**
```
 Database initialized successfully
 Tables created: 7
 Indexes created: 12
 Initial data loaded
```

## Schritt 5: System testen

```bash
# Sicherheitssetup ausführen
python setup_security.py

# System-Health-Check
python test_suite.py

# API-Server starten
python src/main_simple.py
```

**Erfolgreiche Ausgabe:**
```
 Starting Trading System API...
 API Base: http://localhost:5001
 All components healthy
```

## Schritt 6: Dashboard starten

**Neues Terminal öffnen:**
```bash
cd trading-dashboard
npm install
npm run dev
```

**Dashboard-URL:** http://localhost:5174

## Schritt 7: Erste Tests

### API-Test
```bash
curl http://localhost:5001/api/health
```

**Erwartete Antwort:**
```json
{
  "status": "healthy",
  "service": "Trading System API",
  "version": "1.0.0"
}
```

### Dashboard-Test
1. Öffnen Sie http://localhost:5174 im Browser
2. Navigieren Sie zum "Overview" Tab
3. Überprüfen Sie, dass alle Komponenten "Online" anzeigen

### Datensammlung-Test
```bash
python data_collector_v2.py --test
```

## Schritt 8: Erstes Paper Trading

### Signal generieren
```bash
curl -X GET http://localhost:5001/api/signals/recommendations
```

### Test-Order erstellen
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

## Nächste Schritte

### Für Entwickler
- Lesen Sie die vollständige Dokumentation: `TRADING_SYSTEM_DOCUMENTATION.md`
- Erkunden Sie die API-Referenz: `API_REFERENCE.md`
- Führen Sie erweiterte Tests durch: `python test_suite.py --extended`

### Für Trader
- Konfigurieren Sie Ihre bevorzugten Symbole in `config.py`
- Testen Sie verschiedene Trading-Strategien im Paper Trading
- Richten Sie TradingView-Webhooks ein für externe Signale

### Für Produktionsumgebungen
- Folgen Sie dem Deployment-Guide für Docker-Setup
- Konfigurieren Sie SSL/TLS für sichere Verbindungen
- Richten Sie Monitoring und Backups ein

## Häufige Probleme

### Problem: "ModuleNotFoundError"
**Lösung:** Stellen Sie sicher, dass die virtuelle Umgebung aktiviert ist und alle Abhängigkeiten installiert sind.

### Problem: "Database connection failed"
**Lösung:** Überprüfen Sie Dateiberechtigungen im Arbeitsverzeichnis.

### Problem: "API key invalid"
**Lösung:** Überprüfen Sie die .env-Datei und stellen Sie sicher, dass alle Schlüssel korrekt konfiguriert sind.

### Problem: "Port already in use"
**Lösung:** Ändern Sie den Port in der Konfiguration oder stoppen Sie andere Services.

## Support

- **Dokumentation:** `TRADING_SYSTEM_DOCUMENTATION.md`
- **Troubleshooting:** Siehe Abschnitt "Troubleshooting" in der Hauptdokumentation
- **Community:** GitHub Issues für Fragen und Bug-Reports

---

**Herzlichen Glückwunsch!** Ihr Trading-System ist jetzt einsatzbereit. Beginnen Sie mit Paper Trading, um sich mit dem System vertraut zu machen, bevor Sie zu Live Trading wechseln.

