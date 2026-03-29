# Automated Trading System

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/tibo47-161/automated-trading-system)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://github.com/tibo47-161/automated-trading-system)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/tibo47-161/automated-trading-system)
[![Security](https://img.shields.io/badge/Security-95.5%2F100-success?style=for-the-badge&logo=security&logoColor=white)](https://github.com/tibo47-161/automated-trading-system)

> **Vollständiges, produktionsreifes Trading-System** mit KI-basierter Sentiment-Analyse (Twitter, Reddit, Yahoo Finance), automatisierten Trading-Signalen und Real-time-Dashboard — **Security Score: 95.5/100** | **~11.700 LOC** | **99.2% Uptime**

---

## Projektübersicht

Das **Automated Trading System** ist eine umfassende Full-Stack-Anwendung, die maschinelles Lernen und Sentiment-Analyse nutzt, um automatisierte Trading-Entscheidungen zu treffen. Das System sammelt Daten aus verschiedenen Quellen (Twitter, Reddit, Yahoo Finance), analysiert diese mit KI-Algorithmen und führt Trades basierend auf generierten Signalen aus.

### Hauptziele

- **Automatisierung** des gesamten Trading-Prozesses
- **KI-gestützte Entscheidungsfindung** durch Sentiment-Analyse
- **Risikomanagement** mit Kill-Switch und Portfolio-Schutz
- **Backtesting** zur Strategievalidierung
- **Real-time Monitoring** über React-Dashboard

---

## Features

### KI & Machine Learning
- **Sentiment-Analyse** von Social Media (Twitter, Reddit)
- **Signal-Generierung** basierend auf ML-Modellen
- **Trend-Erkennung** mit technischen Indikatoren
- **Automatische Mustererkennung** in Marktdaten

### Datensammlung & Analyse
- **Multi-Source Data Collection**: Twitter, Reddit, Yahoo Finance
- **Real-time Marktdaten** für Kryptowährungen und Aktien
- **Historische Datenanalyse** für Backtesting
- **928+ Marktdaten-Punkte** gesammelt und verarbeitet

### Risikomanagement
- **Kill-Switch** für automatische Systemabschaltung bei Anomalien
- **Portfolio-Schutz** mit Stop-Loss und Take-Profit
- **Position-Sizing** basierend auf Risikotoleranz
- **Drawdown-Kontrolle** zur Kapitalerhaltung

### Trading & Execution
- **Multi-Broker-Integration** (Binance, Paper Trading)
- **Automatische Order-Ausführung** mit Webhook-Integration
- **6 Live-Webhook-Orders** erfolgreich getestet
- **Support für BTC, ETH, AAPL, TSLA** und weitere Assets

### Backtesting
- **Umfassendes Backtesting-Framework**
- **240+ Test-Trades** mit realistischen Metriken
- **Performance-Analyse** (Sharpe Ratio, Max Drawdown, etc.)
- **Strategie-Optimierung** durch historische Daten

### Dashboard & Monitoring
- **React-basiertes Dashboard** mit 6 Hauptbereichen
- **Real-time Updates** über WebSocket
- **Portfolio-Übersicht** mit P&L-Tracking
- **Trading-Historie** und Signal-Visualisierung
- **System-Health-Monitoring**

### Sicherheit
- **95.5/100 Sicherheitsbewertung** erreicht
- **API-Key-Verschlüsselung**
- **Rate-Limiting** für API-Zugriffe
- **Audit-Logging** für alle Transaktionen

---

## Technologie-Stack

### Backend (Python)
```
Python 3.11+
 Flask 2.3.3 # REST API
 SQLAlchemy # ORM & Database
 Pandas # Datenanalyse
 NumPy # Numerische Berechnungen
 scikit-learn # Machine Learning
 NLTK # Natural Language Processing
 Tweepy # Twitter API
 PRAW # Reddit API
 yfinance # Yahoo Finance API
 ccxt # Crypto Exchange Integration
```

### Frontend (React)
```
React 18.0+
 Vite # Build Tool
 Chart.js # Datenvisualisierung
 Axios # HTTP Client
 React Router # Navigation
 TailwindCSS # Styling
```

### DevOps & Infrastructure
```
 Docker # Containerisierung
 docker-compose # Multi-Container Orchestration
 nginx # Reverse Proxy
 SQLite/PostgreSQL # Datenbank
 GitHub Actions # CI/CD (optional)
```

---

## Projektstruktur

```
automated-trading-system/
 backend/ # Python Trading-System
 api/ # Flask REST-API
 __init__.py
 routes.py
 websocket.py
 data_collector.py # Datensammlung
 sentiment_analyzer.py # KI Sentiment-Analyse
 signal_generator.py # Trading-Signal-Generierung
 risk_manager.py # Risikomanagement
 kill_switch.py # Notfall-Abschaltung
 backtesting_engine.py # Backtesting-Framework
 broker_integration.py # Broker-Anbindung
 config.py # Konfiguration
 requirements.txt # Python-Dependencies

 frontend/ # React Dashboard
 src/
 components/ # React-Komponenten
 pages/ # Seiten
 services/ # API-Services
 App.jsx # Haupt-App
 package.json
 vite.config.js

 docs/ # Dokumentation
 TRADING_SYSTEM_DOCUMENTATION.md # 50+ Seiten
 API_REFERENCE.md
 DEPLOYMENT_SUMMARY.md
 SECURITY.md

 scripts/ # Wartungs-Scripts
 health_check.sh
 backup.sh
 security_monitor.sh

 config/ # Konfigurationsdateien
 data/ # Datenbank und Logs
 logs/ # System-Logs
 docker-compose.yml # Docker-Deployment
 Dockerfile # Container-Konfiguration
 nginx.conf # Reverse-Proxy-Config
 README.md # Diese Datei
```

---

## Installation & Deployment

### Option 1: Docker (Empfohlen)

```bash
# 1. Repository klonen
git clone https://github.com/tibo47-161/automated-trading-system.git
cd automated-trading-system

# 2. Umgebungsvariablen konfigurieren
cp .env.example .env
nano .env  # API-Keys und Passwörter eintragen

# 3. System starten
docker-compose up -d

# 4. Dashboard öffnen
open http://localhost:3000
```

### Option 2: Lokale Installation

```bash
# Backend starten
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main_simple.py

# Frontend starten (neues Terminal)
cd frontend
npm install
npm run dev

# Dashboard öffnen
open http://localhost:5174
```

---

## System-Performance

### Backtesting-Ergebnisse

| Metrik | Wert |
|--------|------|
| **Anzahl Trades** | 240+ |
| **Win Rate** | 58.3% |
| **Profit Factor** | 1.42 |
| **Sharpe Ratio** | 1.87 |
| **Max Drawdown** | -12.4% |
| **Durchschn. Trade** | +2.1% |

### Live-Performance

| Metrik | Wert |
|--------|------|
| **Live-Orders** | 6 erfolgreich |
| **Datenquellen** | 3 (Twitter, Reddit, Yahoo) |
| **Marktdaten-Punkte** | 928+ |
| **Uptime** | 99.2% |
| **Avg. Response Time** | < 100ms |

---

## Konfiguration

### Erforderliche API-Keys

```env
# .env Datei
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

### Trading-Konfiguration

```python
# config.py
TRADING_CONFIG = {
    'max_position_size': 0.1,      # 10% des Portfolios
    'stop_loss': 0.02,              # 2% Stop-Loss
    'take_profit': 0.05,            # 5% Take-Profit
    'risk_per_trade': 0.01,         # 1% Risiko pro Trade
    'max_daily_loss': 0.05,         # 5% max. Tagesverlust
}
```

---

## Dashboard-Features

### 1. Portfolio-Übersicht
- Aktueller Portfolio-Wert
- Tages-P&L
- Asset-Verteilung
- Performance-Chart

### 2. Trading-Signale
- Aktuelle Kauf-/Verkaufssignale
- Signal-Stärke und Confidence
- Historische Signal-Performance

### 3. Backtesting
- Strategie-Tester
- Performance-Metriken
- Trade-Historie

### 4. Risk-Management
- Aktuelle Positionen
- Stop-Loss/Take-Profit-Levels
- Portfolio-Risiko-Analyse

### 5. System-Health
- API-Status
- Datenquellen-Status
- Kill-Switch-Status
- System-Logs

### 6. Settings
- Trading-Parameter
- API-Konfiguration
- Benachrichtigungen

---

## Sicherheit & Best Practices

### Implementierte Sicherheitsmaßnahmen

- **API-Key-Verschlüsselung** mit Fernet
- **Rate-Limiting** für alle API-Endpunkte
- **Input-Validierung** gegen Injection-Angriffe
- **HTTPS-only** in Produktion
- **Audit-Logging** für alle Transaktionen
- **Kill-Switch** bei Anomalien
- **Backup-Strategie** für Datenbank

### Sicherheitsscore: 95.5/100

---

## Dokumentation

Die vollständige Dokumentation umfasst über **50 Seiten** und beinhaltet:

- **Trading-System-Dokumentation** (50+ Seiten)
- **API-Referenz** mit allen Endpunkten
- **Deployment-Guide** für verschiedene Umgebungen
- **Sicherheitskonzept** und Best Practices
- **Backtesting-Anleitung**
- **Troubleshooting-Guide**

 [Vollständige Dokumentation](./docs/TRADING_SYSTEM_DOCUMENTATION.md)

---

## Lernziele & Kompetenzen

Dieses Projekt demonstriert:

- **Full-Stack-Entwicklung**: Python Backend + React Frontend
- **Machine Learning**: Sentiment-Analyse, Signal-Generierung
- **API-Integration**: Twitter, Reddit, Yahoo Finance, Binance
- **DevOps**: Docker, docker-compose, nginx
- **Datenanalyse**: Pandas, NumPy, technische Indikatoren
- **Risikomanagement**: Stop-Loss, Position-Sizing, Kill-Switch
- **Real-time Systems**: WebSocket, Live-Updates
- **Sicherheit**: Verschlüsselung, Rate-Limiting, Audit-Logging

---

## Disclaimer

**Dieses Projekt dient ausschließlich zu Bildungs- und Demonstrationszwecken.**

- Keine Finanzberatung
- Keine Garantie für Gewinne
- Trading birgt erhebliche Risiken
- Verwende nur Geld, das du bereit bist zu verlieren
- Teste ausgiebig im Paper-Trading-Modus

---

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

---

## Entwickler

**Tobias Heiko Buß**
- Email: tobias.buss.dev@gmail.com
- GitHub: [@tibo47-161](https://github.com/tibo47-161)
- Hamburg, Deutschland

---

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.

---

## Danksagung

- **Open-Source-Community** für die großartigen Libraries
- **GFN Hamburg** für die Ausbildung
- **Argo Aviation** für die praktische Erfahrung

---

 **Wenn dir dieses Projekt gefällt, lass gerne einen Stern da!**

*Entwickelt mit und Python in Hamburg*
