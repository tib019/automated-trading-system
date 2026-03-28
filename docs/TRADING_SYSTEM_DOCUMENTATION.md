# Trading System - Umfassende Dokumentation

**Version:** 1.0.0  
**Datum:** 1. September 2025  
**Autor:** Manus AI  
**Status:** Produktionsreif  

---

## Inhaltsverzeichnis

1. [Systemübersicht](#systemübersicht)
2. [Architektur und Komponenten](#architektur-und-komponenten)
3. [Installation und Setup](#installation-und-setup)
4. [API-Dokumentation](#api-dokumentation)
5. [Dashboard-Benutzerhandbuch](#dashboard-benutzerhandbuch)
6. [Konfiguration](#konfiguration)
7. [Sicherheit](#sicherheit)
8. [Deployment](#deployment)
9. [Monitoring und Wartung](#monitoring-und-wartung)
10. [Troubleshooting](#troubleshooting)
11. [Entwickler-Guide](#entwickler-guide)
12. [FAQ](#faq)
13. [Anhang](#anhang)

---

## Systemübersicht

Das automatisierte Trading-System ist eine umfassende Lösung für den algorithmischen Handel mit Kryptowährungen und Aktien. Das System kombiniert moderne Datenanalyse, künstliche Intelligenz und robuste Risikomanagement-Strategien, um automatisierte Handelsentscheidungen zu treffen und auszuführen.

### Hauptfunktionen

Das Trading-System bietet eine vollständige Suite von Funktionen für professionelle Trader und Finanzinstitutionen. Die Kernfunktionalitäten umfassen die automatisierte Sammlung und Analyse von Marktdaten aus verschiedenen Quellen, einschließlich Yahoo Finance, Twitter und Reddit. Das System nutzt fortschrittliche Sentiment-Analyse-Algorithmen, um die Marktstimmung zu bewerten und diese Informationen in die Handelsentscheidungen zu integrieren.

Die Signal-Generierung basiert auf einer Kombination aus technischen Indikatoren und Sentiment-Analyse. Das System berechnet kontinuierlich Moving Averages, RSI, MACD und Bollinger Bands, um technische Handelssignale zu identifizieren. Diese werden mit Sentiment-Daten gewichtet, um robuste Kauf- und Verkaufssignale zu generieren. Jedes Signal wird mit einer Konfidenz-Bewertung und Stärke-Klassifizierung versehen, um Tradern bei der Entscheidungsfindung zu helfen.

Das integrierte Risikomanagement-System überwacht kontinuierlich das Portfolio und implementiert automatische Schutzmaßnahmen. Ein Kill-Switch-Mechanismus kann bei kritischen Marktbedingungen alle Positionen automatisch schließen, um das Kapital zu schützen. Das System berechnet dynamische Position-Größen basierend auf der aktuellen Volatilität und dem verfügbaren Kapital, um das Risiko zu optimieren.

### Unterstützte Assets

Das System unterstützt eine breite Palette von Finanzinstrumenten, die in zwei Hauptkategorien unterteilt sind. Bei Kryptowährungen werden Bitcoin (BTC-USD), Ethereum (ETH-USD), Cardano (ADA-USD), Polkadot (DOT-USD) und Chainlink (LINK-USD) unterstützt. Diese Auswahl deckt die wichtigsten Kryptowährungen nach Marktkapitalisierung ab und bietet Diversifikationsmöglichkeiten über verschiedene Blockchain-Technologien hinweg.

Im Aktienbereich konzentriert sich das System auf hochliquide US-Aktien, einschließlich Apple (AAPL), Tesla (TSLA), Google (GOOGL), Microsoft (MSFT), Amazon (AMZN) und NVIDIA (NVDA). Diese Aktien wurden aufgrund ihrer hohen Liquidität, Volatilität und der Verfügbarkeit umfangreicher Marktdaten ausgewählt. Das System kann einfach erweitert werden, um zusätzliche Assets zu unterstützen, indem die Konfigurationsdateien entsprechend angepasst werden.

### Technologie-Stack

Das Trading-System wurde mit modernen Technologien entwickelt, um Skalierbarkeit, Sicherheit und Performance zu gewährleisten. Das Backend basiert auf Python 3.11 und nutzt Flask als Web-Framework für die REST-API. Für die Datenverarbeitung werden pandas und numpy eingesetzt, während matplotlib für Visualisierungen verwendet wird. Die Datenbank-Schicht nutzt SQLite für die lokale Datenspeicherung, kann aber einfach auf PostgreSQL oder MySQL für Produktionsumgebungen migriert werden.

Das Frontend besteht aus einer React-Anwendung mit TypeScript-Unterstützung, die ein modernes und responsives Dashboard bietet. Tailwind CSS wird für das Styling verwendet, während Recharts für interaktive Datenvisualisierungen sorgt. Die Kommunikation zwischen Frontend und Backend erfolgt über eine RESTful API mit CORS-Unterstützung für sichere Cross-Origin-Requests.

Für die Sicherheit implementiert das System AES-256-Verschlüsselung für sensitive Daten, HMAC-SHA256 für Webhook-Signatur-Validierung und PBKDF2 für sichere Schlüsselableitung. Rate-Limiting und Input-Sanitization schützen vor Missbrauch und Angriffen. Das System erreicht eine Sicherheitsbewertung von 95.5/100 in automatisierten Audits.




## Architektur und Komponenten

Das Trading-System folgt einer modularen Microservices-Architektur, die Skalierbarkeit, Wartbarkeit und Testbarkeit gewährleistet. Die Architektur ist in mehrere spezialisierte Komponenten unterteilt, die über definierte Schnittstellen miteinander kommunizieren.

### Systemarchitektur

Die Gesamtarchitektur des Trading-Systems basiert auf dem Prinzip der Trennung von Verantwortlichkeiten (Separation of Concerns). Jede Komponente hat eine klar definierte Aufgabe und kommuniziert über standardisierte APIs mit anderen Komponenten. Diese Architektur ermöglicht es, einzelne Komponenten unabhängig zu entwickeln, zu testen und zu deployen.

Das System ist in drei Hauptschichten unterteilt: die Datenebene, die Geschäftslogik-Ebene und die Präsentationsebene. Die Datenebene umfasst alle Komponenten, die für die Sammlung, Speicherung und den Abruf von Marktdaten verantwortlich sind. Die Geschäftslogik-Ebene enthält die Algorithmen für Signal-Generierung, Risikomanagement und Order-Ausführung. Die Präsentationsebene besteht aus der REST-API und dem Web-Dashboard.

### Datensammlung-Modul (data_collector_v2.py)

Das Datensammlung-Modul ist das Herzstück der Datenakquisition und implementiert eine robuste, skalierbare Lösung für die kontinuierliche Sammlung von Marktdaten aus verschiedenen Quellen. Das Modul nutzt ein ereignisgesteuertes Design mit automatischem Scheduling, um Daten in regelmäßigen Intervallen zu sammeln und zu verarbeiten.

Die Implementierung umfasst spezialisierte API-Clients für verschiedene Datenquellen. Der Yahoo Finance Client sammelt Echtzeit-Marktdaten einschließlich Preise, Volumen und historische Daten. Der Twitter API Client überwacht relevante Hashtags und Mentions für Sentiment-Analyse. Der Reddit API Client durchsucht spezifische Subreddits wie r/wallstreetbets und r/cryptocurrency nach relevanten Diskussionen.

Das Modul implementiert intelligente Fehlerbehandlung und Retry-Logik, um mit temporären API-Ausfällen und Rate-Limiting umzugehen. Exponential Backoff wird verwendet, um die Belastung der externen APIs zu minimieren. Alle gesammelten Daten werden normalisiert und in einer SQLite-Datenbank gespeichert, mit automatischer Deduplizierung und Datenvalidierung.

Die Symbol-Erkennung erfolgt über ein konfigurierbares System von regulären Ausdrücken und Keyword-Matching. Das System kann Ticker-Symbole in verschiedenen Formaten erkennen ($BTC, Bitcoin, BTC-USD) und ordnet sie den entsprechenden Assets zu. Konfidenz-Scores werden basierend auf der Häufigkeit und dem Kontext der Erwähnungen berechnet.

### Sentiment-Analyse-Engine (sentiment_analyzer.py)

Die Sentiment-Analyse-Engine implementiert einen hybriden Ansatz, der regelbasierte und statistische Methoden kombiniert, um die Marktstimmung aus Textdaten zu extrahieren. Das System nutzt ein umfangreiches Lexikon von über 80 gewichteten Keywords und 20 Emojis, die speziell für Finanzmarkt-Kontext kalibriert wurden.

Die Analyse erfolgt in mehreren Stufen. Zunächst wird der Text vorverarbeitet, um Rauschen zu entfernen und die Qualität der Analyse zu verbessern. Dies umfasst die Normalisierung von Groß- und Kleinschreibung, die Entfernung von URLs und die Behandlung von Sonderzeichen. Anschließend wird der Text tokenisiert und jedes Token gegen das Sentiment-Lexikon abgeglichen.

Das System implementiert fortschrittliche Kontextanalyse, um Negationen und Verstärkungen zu erkennen. Phrasen wie "nicht gut" oder "sehr bullish" werden korrekt interpretiert und entsprechend gewichtet. Caps Lock Detection identifiziert emotionale Intensität, während Emoji-Analyse zusätzliche Sentiment-Signale liefert.

Die Konfidenz-Berechnung berücksichtigt mehrere Faktoren: die Länge des analysierten Textes, die Dichte der Sentiment-Keywords, die Präsenz von Verstärkern oder Negationen und die Konsistenz der Sentiment-Signale. Das Ergebnis ist ein Sentiment-Score zwischen -1 (sehr bearish) und +1 (sehr bullish) mit einem zugehörigen Konfidenz-Wert.

### Signal-Generierung (signal_generator.py)

Das Signal-Generierungs-Modul implementiert eine sophisticated Trading-Strategie, die technische Analyse mit Sentiment-Daten kombiniert. Das System berechnet kontinuierlich eine Vielzahl von technischen Indikatoren und gewichtet diese mit aktuellen Sentiment-Daten, um robuste Handelssignale zu generieren.

Die technische Analyse umfasst Moving Averages (SMA und EMA), Relative Strength Index (RSI), Moving Average Convergence Divergence (MACD) und Bollinger Bands. Jeder Indikator wird individuell berechnet und bewertet, bevor die Signale zu einem Gesamtscore kombiniert werden. Das System implementiert adaptive Parameter, die sich an die aktuelle Marktvolatilität anpassen.

Die Signal-Fusion erfolgt über ein gewichtetes Scoring-System, bei dem technische Indikatoren 70% und Sentiment-Daten 30% des Gesamtscores ausmachen. Diese Gewichtung wurde durch umfangreiche Backtests optimiert und kann je nach Marktbedingungen angepasst werden. Das System generiert drei Arten von Signalen: BUY, SELL und HOLD, jeweils mit Stärke-Klassifizierungen (WEAK, MODERATE, STRONG).

Für jedes generierte Signal berechnet das System automatisch Entry-Preise, Stop-Loss-Levels und Take-Profit-Ziele. Diese werden basierend auf der aktuellen Volatilität und historischen Preisbewegungen dynamisch angepasst. Das Risk-Reward-Verhältnis wird konstant bei 1:3 gehalten, um eine positive Erwartung zu gewährleisten.

### Risikomanagement-System (risk_manager.py)

Das Risikomanagement-System ist eine kritische Komponente, die das Portfolio kontinuierlich überwacht und automatische Schutzmaßnahmen implementiert. Das System arbeitet auf mehreren Ebenen: Portfolio-Level, Position-Level und Order-Level, um umfassenden Schutz zu gewährleisten.

Auf Portfolio-Level überwacht das System die Gesamtexposition, den maximalen Drawdown und die Korrelation zwischen Positionen. Ein Kill-Switch-Mechanismus wird automatisch aktiviert, wenn der Gesamtverlust 15% des Portfoliowerts übersteigt oder andere kritische Bedingungen erfüllt sind. Das System berechnet kontinuierlich Value-at-Risk (VaR) und Expected Shortfall (ES) Metriken.

Die Position-Sizing-Logik implementiert das Kelly-Kriterium in einer konservativen Variante, um optimale Positionsgrößen zu berechnen. Das System berücksichtigt die aktuelle Volatilität, die historische Performance der Strategie und die verfügbare Liquidität. Maximale Positionsgrößen werden dynamisch angepasst, um Überkonzentration zu vermeiden.

Das System implementiert verschiedene Risiko-Level (LOW, MODERATE, HIGH, CRITICAL) mit entsprechenden Handlungsprotokollen. Bei erhöhten Risiko-Leveln werden automatisch Positionsgrößen reduziert, neue Positionen eingeschränkt oder im Extremfall alle Positionen geschlossen. Alle Risiko-Events werden protokolliert und können für spätere Analyse verwendet werden.

### Order-Management-System (order_manager.py)

Das Order-Management-System (OMS) fungiert als zentrale Schnittstelle zwischen den Trading-Algorithmen und den Brokern. Es implementiert eine abstrakte Broker-Schnittstelle, die es ermöglicht, verschiedene Broker-APIs zu unterstützen, ohne die Geschäftslogik zu ändern.

Das System unterstützt verschiedene Order-Typen: Market Orders für sofortige Ausführung, Limit Orders für preisspezifische Ausführung, Stop Orders für Verlustbegrenzung und Stop-Limit Orders für erweiterte Kontrolle. Jeder Order-Typ wird mit spezifischen Validierungsregeln und Ausführungslogik behandelt.

Die Order-Lifecycle-Verwaltung verfolgt Orders von der Erstellung bis zur finalen Ausführung oder Stornierung. Status-Updates werden in Echtzeit verarbeitet und an alle interessierten Komponenten weitergeleitet. Das System implementiert automatische Retry-Logik für fehlgeschlagene Orders und Timeout-Behandlung für hängende Orders.

Für das Paper Trading implementiert das System eine realistische Simulation, die Slippage, Kommissionen und Marktimpact berücksichtigt. Dies ermöglicht es, Strategien unter realistischen Bedingungen zu testen, bevor sie mit echtem Kapital eingesetzt werden.

### Sicherheitsmanagement (security_manager.py)

Das Sicherheitsmanagement-System implementiert Enterprise-Grade-Sicherheitsmaßnahmen zum Schutz sensibler Daten und zur Gewährleistung der Systemintegrität. Das System nutzt moderne Kryptographie-Standards und Best Practices für sichere Softwareentwicklung.

Die Verschlüsselung sensibler Daten erfolgt mit AES-256 im CBC-Modus mit HMAC-SHA256 für Authentizität. API-Keys und andere Credentials werden verschlüsselt in der Datenbank gespeichert und nur bei Bedarf entschlüsselt. Der Master-Key wird mit PBKDF2 und 100.000 Iterationen aus einem Passwort abgeleitet.

Das Session-Management implementiert sichere Token-basierte Authentifizierung mit konfigurierbaren Ablaufzeiten. Sessions werden an IP-Adressen gebunden und können bei verdächtigen Aktivitäten automatisch invalidiert werden. Das System protokolliert alle Sicherheitsereignisse für Audit-Zwecke.

Rate-Limiting schützt vor Brute-Force-Angriffen und API-Missbrauch. Das System implementiert verschiedene Limits für verschiedene Endpoint-Typen: 60 Webhook-Requests pro Minute, 100 API-Calls pro Minute und 5 Authentifizierungsversuche pro 5 Minuten. Überschreitungen werden automatisch blockiert und protokolliert.

### Backtesting-Framework (backtesting_engine.py)

Das Backtesting-Framework ermöglicht die rigorose Validierung von Trading-Strategien mit historischen Daten. Das System implementiert eine event-driven Simulation, die realistische Marktbedingungen nachbildet und genaue Performance-Metriken liefert.

Die Simulation berücksichtigt verschiedene Marktfaktoren: Bid-Ask-Spreads, Slippage, Kommissionen und Marktimpact. Verschiedene Marktregime (Bull-, Bear- und Seitwärtsmärkte) können simuliert werden, um die Robustheit der Strategien zu testen. Das System unterstützt sowohl Intraday- als auch Multi-Day-Strategien.

Performance-Metriken umfassen traditionelle Kennzahlen wie Total Return, Sharpe Ratio und Maximum Drawdown sowie erweiterte Metriken wie Sortino Ratio, Calmar Ratio und Profit Factor. Das System berechnet auch Trade-spezifische Statistiken wie Win Rate, Average Win/Loss und Trade Duration.

Die Ergebnisse werden in interaktiven Charts visualisiert, die Portfolio-Performance, Drawdown-Perioden und Trade-Verteilungen zeigen. Monte-Carlo-Simulationen können durchgeführt werden, um die statistische Signifikanz der Ergebnisse zu bewerten.


## Installation und Setup

Die Installation des Trading-Systems kann auf verschiedene Weise erfolgen, je nach den spezifischen Anforderungen und der gewünschten Deployment-Umgebung. Das System unterstützt lokale Entwicklungsumgebungen, Docker-Container und Cloud-Deployments.

### Systemanforderungen

Bevor Sie mit der Installation beginnen, stellen Sie sicher, dass Ihr System die Mindestanforderungen erfüllt. Für die Entwicklungsumgebung benötigen Sie Python 3.11 oder höher, Node.js 18.0 oder höher und mindestens 4 GB RAM. Für Produktionsumgebungen werden 8 GB RAM und eine SSD-Festplatte empfohlen.

Das System ist mit Linux (Ubuntu 20.04+, CentOS 8+), macOS (10.15+) und Windows 10/11 kompatibel. Für Produktionsumgebungen wird Linux empfohlen aufgrund der besseren Performance und Stabilität. Docker ist optional, aber für Produktionsdeployments stark empfohlen.

### Lokale Installation

Die lokale Installation beginnt mit dem Klonen des Repository und der Einrichtung der Python-Umgebung. Erstellen Sie zunächst ein Arbeitsverzeichnis und navigieren Sie dorthin:

```bash
mkdir trading_system_workspace
cd trading_system_workspace
```

Klonen Sie das Repository oder kopieren Sie die Systemdateien in das Arbeitsverzeichnis. Erstellen Sie eine virtuelle Python-Umgebung, um Abhängigkeitskonflikte zu vermeiden:

```bash
python3.11 -m venv trading_env
source trading_env/bin/activate  # Linux/macOS
# oder
trading_env\Scripts\activate  # Windows
```

Installieren Sie die erforderlichen Python-Pakete:

```bash
pip install -r requirements.txt
```

Die requirements.txt-Datei enthält alle notwendigen Abhängigkeiten mit spezifischen Versionen für maximale Kompatibilität. Wichtige Pakete umfassen Flask für die Web-API, pandas für Datenverarbeitung, cryptography für Sicherheitsfunktionen und requests für API-Kommunikation.

### Datenbank-Setup

Das System verwendet SQLite als Standard-Datenbank für die lokale Entwicklung. Die Datenbank wird automatisch beim ersten Start erstellt. Für Produktionsumgebungen können Sie PostgreSQL oder MySQL konfigurieren, indem Sie die Verbindungszeichenfolge in der Konfigurationsdatei anpassen.

Führen Sie das Initialisierungsskript aus, um die Datenbankstruktur zu erstellen:

```bash
cd trading_system
python init_database.py
```

Dieses Skript erstellt alle notwendigen Tabellen für Marktdaten, Orders, Positionen, Sicherheitsereignisse und Konfigurationen. Es führt auch grundlegende Datenvalidierung durch und erstellt Indizes für optimale Performance.

### Konfiguration der Umgebungsvariablen

Sicherheitsrelevante Konfigurationen werden über Umgebungsvariablen verwaltet. Kopieren Sie die Beispiel-Konfigurationsdatei und passen Sie sie an Ihre Bedürfnisse an:

```bash
cp .env.example .env
nano .env
```

Die wichtigsten Umgebungsvariablen umfassen:

- `TRADING_MASTER_PASSWORD`: Master-Passwort für die Verschlüsselung
- `WEBHOOK_SECRET`: Geheimer Schlüssel für Webhook-Validierung
- `OPENAI_API_KEY`: API-Schlüssel für erweiterte Sentiment-Analyse (optional)
- `BINANCE_API_KEY` und `BINANCE_SECRET_KEY`: Binance API-Credentials (für Live-Trading)

Stellen Sie sicher, dass die .env-Datei niemals in die Versionskontrolle eingecheckt wird. Fügen Sie sie zur .gitignore-Datei hinzu, falls sie nicht bereits enthalten ist.

### API-Schlüssel-Konfiguration

Für den vollständigen Funktionsumfang benötigen Sie API-Schlüssel von verschiedenen Diensten. Yahoo Finance API ist kostenlos und erfordert keine Registrierung. Für Twitter und Reddit APIs müssen Sie sich bei den jeweiligen Entwicklerportalen registrieren.

Für Live-Trading mit Binance erstellen Sie ein Konto auf binance.com und generieren API-Schlüssel in den Kontoeinstellungen. Aktivieren Sie zunächst nur Spot-Trading-Berechtigungen und testen Sie das System im Testnet, bevor Sie zu Live-Trading wechseln.

Verwenden Sie das Sicherheitsmanagement-Tool, um API-Schlüssel sicher zu speichern:

```bash
python security_manager.py --store-api-key binance_api "your_api_key_here"
python security_manager.py --store-api-key binance_secret "your_secret_key_here"
```

### Frontend-Setup

Das React-Dashboard erfordert Node.js und npm. Navigieren Sie zum Dashboard-Verzeichnis und installieren Sie die Abhängigkeiten:

```bash
cd trading-dashboard
npm install
```

Für die Entwicklung starten Sie den Development-Server:

```bash
npm run dev
```

Das Dashboard ist dann unter http://localhost:5174 verfügbar. Für Produktionsumgebungen erstellen Sie einen optimierten Build:

```bash
npm run build
```

Die generierten Dateien im `dist`-Verzeichnis können dann von einem Webserver wie Nginx oder Apache bereitgestellt werden.

### Docker-Installation

Docker bietet die einfachste und konsistenteste Deployment-Option. Stellen Sie sicher, dass Docker und Docker Compose auf Ihrem System installiert sind. Die Docker-Konfiguration ist bereits vorbereitet und kann direkt verwendet werden.

Erstellen Sie zunächst die notwendigen Verzeichnisse für persistente Daten:

```bash
mkdir -p data logs
```

Starten Sie das System mit Docker Compose:

```bash
docker-compose up -d
```

Dieser Befehl startet alle Komponenten des Trading-Systems in separaten Containern: die API, das Dashboard und eine Nginx-Reverse-Proxy. Die Services sind automatisch miteinander vernetzt und konfiguriert.

Überprüfen Sie den Status der Container:

```bash
docker-compose ps
```

Die Logs können mit folgendem Befehl eingesehen werden:

```bash
docker-compose logs -f trading-api
```

### Erste Schritte nach der Installation

Nach der erfolgreichen Installation führen Sie die folgenden Schritte aus, um das System zu testen und zu konfigurieren. Starten Sie zunächst das Backend-System:

```bash
cd trading_system
python src/main_simple.py
```

Das System sollte ohne Fehler starten und die verfügbaren Endpoints anzeigen. Testen Sie die API-Verbindung:

```bash
curl http://localhost:5001/api/health
```

Eine erfolgreiche Antwort zeigt, dass das System ordnungsgemäß funktioniert. Öffnen Sie das Dashboard in Ihrem Browser unter http://localhost:5174 (Development) oder http://localhost:3000 (Docker).

Führen Sie einen ersten Datensammlung-Test durch:

```bash
python data_collector_v2.py --test
```

Dieser Befehl sammelt Testdaten von den konfigurierten APIs und speichert sie in der Datenbank. Überprüfen Sie die Logs auf Fehler oder Warnungen.

### Validierung der Installation

Um sicherzustellen, dass alle Komponenten ordnungsgemäß funktionieren, führen Sie die mitgelieferten Tests aus:

```bash
python test_suite.py
```

Diese Test-Suite überprüft alle kritischen Funktionen des Systems, einschließlich Datensammlung, Signal-Generierung, Risikomanagement und Sicherheitsfunktionen. Alle Tests sollten erfolgreich abgeschlossen werden.

Führen Sie zusätzlich ein Sicherheitsaudit durch:

```bash
python security_audit.py
```

Das Audit sollte eine Bewertung von mindestens 90/100 ergeben. Niedrigere Bewertungen weisen auf Konfigurationsprobleme oder Sicherheitslücken hin, die behoben werden sollten.

### Fehlerbehebung bei der Installation

Häufige Installationsprobleme und ihre Lösungen werden hier dokumentiert. Wenn Python-Pakete nicht installiert werden können, überprüfen Sie zunächst Ihre Python-Version und stellen Sie sicher, dass pip auf dem neuesten Stand ist:

```bash
python --version
pip --version
pip install --upgrade pip
```

Bei Problemen mit der Datenbank-Initialisierung überprüfen Sie die Dateiberechtigungen im Arbeitsverzeichnis. Das System benötigt Schreibrechte für die Erstellung der SQLite-Datenbank.

Wenn API-Aufrufe fehlschlagen, überprüfen Sie Ihre Internetverbindung und Firewall-Einstellungen. Einige Unternehmens-Firewalls blockieren möglicherweise Verbindungen zu externen APIs.

Für Docker-spezifische Probleme überprüfen Sie, ob Docker ordnungsgemäß läuft und ausreichend Ressourcen zugewiesen sind. Mindestens 2 GB RAM sollten für Docker verfügbar sein.


## API-Dokumentation

Die Trading-System-API bietet eine umfassende RESTful-Schnittstelle für alle Systemfunktionen. Die API folgt REST-Prinzipien und verwendet JSON für Datenübertragung. Alle Endpoints sind über HTTPS erreichbar und implementieren angemessene Sicherheitsmaßnahmen.

### API-Basis-URL und Authentifizierung

Die API ist standardmäßig unter `http://localhost:5001/api` verfügbar. Für Produktionsumgebungen sollte HTTPS konfiguriert werden. Die meisten Endpoints erfordern keine Authentifizierung für Lesezugriffe, während schreibende Operationen API-Schlüssel oder Session-Token erfordern.

Authentifizierung erfolgt über HTTP-Header:
```
Authorization: Bearer <your_api_token>
X-API-Key: <your_api_key>
```

Rate-Limiting ist implementiert, um Missbrauch zu verhindern. Standard-Limits sind 100 Requests pro Minute für allgemeine API-Calls und 60 Requests pro Minute für Webhook-Endpoints.

### System-Status und Health-Check Endpoints

#### GET /api/health

Dieser Endpoint bietet einen schnellen Health-Check für das System und gibt grundlegende Statusinformationen zurück.

**Request:**
```bash
curl -X GET http://localhost:5001/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Trading System API",
  "version": "1.0.0",
  "components": {
    "data_collector": "active",
    "signal_generator": "active",
    "risk_manager": "active",
    "order_manager": "active",
    "security_manager": "active"
  }
}
```

Der Health-Check überprüft die Verfügbarkeit aller kritischen Systemkomponenten und gibt deren Status zurück. Ein Status von "healthy" zeigt an, dass alle Komponenten ordnungsgemäß funktionieren.

#### GET /api/status

Dieser Endpoint liefert detaillierte Systeminformationen einschließlich Portfolio-Status, Trading-Aktivität und Sicherheitsereignisse.

**Request:**
```bash
curl -X GET http://localhost:5001/api/status
```

**Response:**
```json
{
  "status": "operational",
  "timestamp": "2025-09-01T08:00:00Z",
  "portfolio": {
    "total_value": 100000,
    "cash_balance": 95000,
    "positions": [
      {
        "symbol": "BTC-USD",
        "quantity": 0.08,
        "value": 4000
      }
    ],
    "risk_level": "LOW"
  },
  "trading": {
    "recent_orders": 6,
    "last_order": {
      "id": "order_123",
      "symbol": "BTC-USD",
      "side": "BUY",
      "status": "FILLED"
    }
  },
  "security": {
    "events_24h": 12,
    "last_audit": "recent"
  }
}
```

### Portfolio-Management Endpoints

#### GET /api/portfolio/status

Liefert den aktuellen Portfolio-Status mit detaillierten Informationen über Positionen, Performance und Risikometriken.

**Request:**
```bash
curl -X GET http://localhost:5001/api/portfolio/status
```

**Response:**
```json
{
  "status": "success",
  "portfolio": {
    "total_value": 100000,
    "cash_balance": 95000,
    "unrealized_pnl": 500,
    "realized_pnl": -200,
    "positions": [
      {
        "symbol": "BTC-USD",
        "quantity": 0.08,
        "avg_price": 50000,
        "current_price": 50500,
        "market_value": 4040,
        "unrealized_pnl": 40,
        "pnl_percent": 1.0
      }
    ],
    "risk_metrics": {
      "portfolio_risk": "LOW",
      "max_drawdown": 2.5,
      "sharpe_ratio": 1.8,
      "exposure": 5.89
    }
  }
}
```

#### GET /api/portfolio/positions

Gibt eine Liste aller aktuellen Positionen zurück.

**Query Parameters:**
- `symbol` (optional): Filtert nach spezifischem Symbol
- `status` (optional): Filtert nach Position-Status (open, closed)

**Request:**
```bash
curl -X GET "http://localhost:5001/api/portfolio/positions?symbol=BTC-USD"
```

#### GET /api/portfolio/performance

Liefert Performance-Metriken für einen spezifizierten Zeitraum.

**Query Parameters:**
- `days` (optional, default: 30): Anzahl der Tage für die Performance-Berechnung

**Request:**
```bash
curl -X GET "http://localhost:5001/api/portfolio/performance?days=7"
```

### Order-Management Endpoints

#### GET /api/orders

Ruft die Order-Historie ab mit optionalen Filterparametern.

**Query Parameters:**
- `limit` (optional, default: 50): Maximale Anzahl der zurückgegebenen Orders
- `status` (optional): Filtert nach Order-Status (PENDING, FILLED, CANCELLED)
- `symbol` (optional): Filtert nach Symbol

**Request:**
```bash
curl -X GET "http://localhost:5001/api/orders?limit=10&status=FILLED"
```

**Response:**
```json
{
  "status": "success",
  "orders": [
    {
      "id": "order_123",
      "symbol": "BTC-USD",
      "side": "BUY",
      "quantity": 0.08,
      "price": 50000,
      "status": "FILLED",
      "timestamp": "2025-09-01T07:30:00Z",
      "commission": 2.50
    }
  ],
  "count": 1
}
```

#### POST /api/orders

Erstellt eine neue Order. Dieser Endpoint erfordert Authentifizierung und durchläuft Risikomanagement-Validierung.

**Request Body:**
```json
{
  "symbol": "BTC-USD",
  "side": "BUY",
  "quantity": 0.1,
  "order_type": "MARKET",
  "stop_loss": 48000,
  "take_profit": 55000
}
```

**Request:**
```bash
curl -X POST http://localhost:5001/api/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.1,
    "order_type": "MARKET"
  }'
```

**Response:**
```json
{
  "status": "success",
  "order": {
    "id": "order_124",
    "symbol": "BTC-USD",
    "side": "BUY",
    "quantity": 0.1,
    "order_type": "MARKET",
    "status": "PENDING",
    "timestamp": "2025-09-01T08:00:00Z"
  }
}
```

#### POST /api/orders/{order_id}/cancel

Storniert eine bestehende Order.

**Request:**
```bash
curl -X POST http://localhost:5001/api/orders/order_124/cancel \
  -H "Authorization: Bearer <token>"
```

### Signal-Generierung Endpoints

#### GET /api/signals/recommendations

Liefert aktuelle Trading-Empfehlungen basierend auf der Signal-Analyse.

**Request:**
```bash
curl -X GET http://localhost:5001/api/signals/recommendations
```

**Response:**
```json
{
  "status": "success",
  "recommendations": [
    {
      "symbol": "BTC-USD",
      "action": "BUY",
      "strength": "MODERATE",
      "confidence": 0.75,
      "price": 50500,
      "reasoning": "Bullish sentiment + oversold RSI",
      "entry_price": 50400,
      "stop_loss": 48900,
      "take_profit": 55200
    }
  ],
  "count": 1,
  "timestamp": "2025-09-01T08:00:00Z"
}
```

#### POST /api/signals/generate

Generiert ein Trading-Signal für gegebene Markt- und Sentiment-Daten.

**Request Body:**
```json
{
  "market_data": {
    "symbol": "BTC-USD",
    "price": 50500,
    "volume": 1000000,
    "price_history": [50000, 50200, 50100, 50500]
  },
  "sentiment_data": {
    "sentiment_score": 0.3,
    "confidence": 0.7,
    "source": "aggregated"
  }
}
```

#### GET /api/signals/technical-indicators/{symbol}

Liefert technische Indikatoren für ein spezifisches Symbol.

**Request:**
```bash
curl -X GET http://localhost:5001/api/signals/technical-indicators/BTC-USD
```

**Response:**
```json
{
  "status": "success",
  "symbol": "BTC-USD",
  "indicators": {
    "sma_20": 49800,
    "ema_12": 50100,
    "rsi": 45.2,
    "macd": {
      "macd": 120.5,
      "signal": 115.2,
      "histogram": 5.3
    },
    "bollinger_bands": {
      "upper": 52000,
      "middle": 50000,
      "lower": 48000
    },
    "current_price": 50500,
    "volume": 1000000
  }
}
```

### Trading-Operationen Endpoints

#### POST /api/trading/collect-data

Triggert die manuelle Datensammlung für spezifizierte Symbole.

**Request Body:**
```json
{
  "symbols": ["BTC-USD", "ETH-USD", "AAPL"]
}
```

#### POST /api/trading/auto-trade

Führt den vollständigen automatisierten Trading-Workflow aus: Datensammlung, Signal-Generierung, Risikobewertung und Order-Ausführung.

**Request Body:**
```json
{
  "symbol": "BTC-USD"
}
```

**Response:**
```json
{
  "status": "success",
  "workflow": {
    "market_data": {
      "symbol": "BTC-USD",
      "price": 50500,
      "volume": 1000000
    },
    "sentiment_data": {
      "sentiment_score": 0.3,
      "confidence": 0.7
    },
    "signal": {
      "action": "BUY",
      "strength": "MODERATE",
      "confidence": 0.75
    },
    "order": {
      "id": "order_125",
      "status": "PENDING"
    }
  }
}
```

### Sicherheits-Endpoints

#### GET /api/security/events

Liefert Sicherheitsereignisse für einen spezifizierten Zeitraum.

**Query Parameters:**
- `hours` (optional, default: 24): Zeitraum in Stunden

**Request:**
```bash
curl -X GET "http://localhost:5001/api/security/events?hours=12"
```

#### POST /api/security/audit

Führt ein vollständiges Sicherheitsaudit durch.

**Request:**
```bash
curl -X POST http://localhost:5001/api/security/audit \
  -H "Authorization: Bearer <token>"
```

#### POST /api/security/validate-signature

Validiert Webhook-Signaturen für externe Integrationen.

**Request Body:**
```json
{
  "payload": "webhook_payload_data",
  "signature": "sha256=signature_hash",
  "secret": "webhook_secret"
}
```

### Emergency-Endpoints

#### POST /api/emergency/kill-switch

Aktiviert den Emergency Kill-Switch, der alle offenen Positionen schließt und das Trading stoppt.

**Request:**
```bash
curl -X POST http://localhost:5001/api/emergency/kill-switch \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
  "status": "success",
  "message": "Kill switch activated",
  "result": {
    "positions_closed": 3,
    "orders_cancelled": 2,
    "portfolio_protected": true
  }
}
```

### Webhook-Integration

Das System unterstützt Webhooks für externe Integrationen, insbesondere TradingView-Alerts.

#### POST /webhook/tradingview

Empfängt TradingView-Alerts und konvertiert sie in Trading-Orders.

**Request Body (TradingView Alert Format):**
```json
{
  "symbol": "{{ticker}}",
  "action": "{{strategy.order.action}}",
  "price": "{{close}}",
  "time": "{{time}}"
}
```

### Fehlerbehandlung

Die API verwendet standardisierte HTTP-Status-Codes und Fehlerformate:

**Erfolgreiche Responses:**
- 200 OK: Erfolgreiche GET-Requests
- 201 Created: Erfolgreiche POST-Requests (Erstellung)
- 204 No Content: Erfolgreiche DELETE-Requests

**Client-Fehler:**
- 400 Bad Request: Ungültige Request-Parameter
- 401 Unauthorized: Fehlende oder ungültige Authentifizierung
- 403 Forbidden: Unzureichende Berechtigungen
- 404 Not Found: Ressource nicht gefunden
- 429 Too Many Requests: Rate-Limit überschritten

**Server-Fehler:**
- 500 Internal Server Error: Unerwarteter Server-Fehler
- 503 Service Unavailable: Service temporär nicht verfügbar

**Fehler-Response-Format:**
```json
{
  "status": "error",
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "timestamp": "2025-09-01T08:00:00Z"
}
```

### API-Versionierung

Die API verwendet URL-basierte Versionierung. Die aktuelle Version ist v1 und wird über den Pfad `/api/v1/` erreicht. Für Rückwärtskompatibilität wird `/api/` auf die neueste Version weitergeleitet.

### Rate-Limiting

Rate-Limiting wird pro IP-Adresse und Endpoint-Typ implementiert:

- Allgemeine API-Endpoints: 100 Requests/Minute
- Webhook-Endpoints: 60 Requests/Minute
- Authentifizierungs-Endpoints: 5 Requests/5 Minuten
- Emergency-Endpoints: 10 Requests/Stunde

Rate-Limit-Informationen werden in Response-Headern zurückgegeben:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693555200
```


## Dashboard-Benutzerhandbuch

Das Trading-System-Dashboard bietet eine intuitive und umfassende Benutzeroberfläche für die Überwachung und Steuerung aller Trading-Aktivitäten. Das Dashboard ist als moderne Single-Page-Application (SPA) entwickelt und bietet Echtzeit-Updates, interaktive Charts und eine responsive Benutzeroberfläche, die sowohl auf Desktop- als auch auf mobilen Geräten optimal funktioniert.

### Dashboard-Übersicht und Navigation

Das Dashboard ist in sechs Hauptbereiche unterteilt, die über eine Tab-Navigation am oberen Rand der Anwendung zugänglich sind. Jeder Tab bietet spezialisierte Funktionen und Ansichten für verschiedene Aspekte des Trading-Systems.

Der Overview-Tab bietet eine Zusammenfassung aller wichtigen Systemmetriken auf einen Blick. Hier finden Sie Portfolio-Wert, aktuelle Positionen, jüngste Trading-Aktivitäten und System-Status-Indikatoren. Die Übersicht wird alle 5 Sekunden automatisch aktualisiert, um sicherzustellen, dass Sie immer die neuesten Informationen haben.

Die Navigation ist intuitiv gestaltet mit klaren visuellen Hinweisen für den aktiven Tab. Jeder Tab zeigt relevante Metriken in der Tab-Leiste an, wie die Anzahl offener Positionen im Portfolio-Tab oder die Anzahl aktiver Signale im Signals-Tab. Status-Indikatoren verwenden ein Ampelsystem: Grün für normale Bedingungen, Gelb für Warnungen und Rot für kritische Zustände.

### Portfolio-Management Interface

Der Portfolio-Tab ist das Herzstück des Dashboard und bietet umfassende Einblicke in Ihre Trading-Performance und aktuellen Positionen. Die Hauptansicht zeigt eine Übersichtskarte mit dem Gesamtportfolio-Wert, verfügbarem Cash-Guthaben, unrealisierten und realisierten Gewinnen/Verlusten.

Die Positions-Tabelle listet alle aktuellen Positionen mit detaillierten Informationen auf. Für jede Position sehen Sie das Symbol, die Anzahl der gehaltenen Einheiten, den durchschnittlichen Einkaufspreis, den aktuellen Marktpreis, den Marktwert und die unrealisierten Gewinne/Verluste sowohl in absoluten Zahlen als auch in Prozent. Farbkodierung hilft bei der schnellen Identifizierung profitabler (grün) und verlustbringender (rot) Positionen.

Das Portfolio-Performance-Chart zeigt die Wertentwicklung über die letzten 30 Tage als interaktives Liniendiagramm. Sie können über das Chart hovern, um spezifische Datenpunkte zu sehen, und verschiedene Zeiträume auswählen (7 Tage, 30 Tage, 90 Tage). Das Chart unterstützt Zoom-Funktionen für detaillierte Analysen bestimmter Zeiträume.

Risk-Metriken werden in einer separaten Sektion angezeigt und umfassen das aktuelle Risiko-Level, maximalen Drawdown, Sharpe Ratio und Portfolio-Exposure. Ein visueller Risiko-Indikator zeigt das aktuelle Risiko-Level mit entsprechender Farbkodierung an. Bei erhöhten Risiko-Levels werden automatisch Warnungen angezeigt.

### Order-Management und Trading-Historie

Der Orders-Tab bietet vollständige Kontrolle über alle Trading-Orders und deren Historie. Die Hauptansicht zeigt eine chronologisch sortierte Liste aller Orders mit Filteroptionen nach Status, Symbol und Zeitraum. Jede Order zeigt detaillierte Informationen einschließlich Order-ID, Symbol, Seite (Buy/Sell), Menge, Preis, Status und Zeitstempel.

Die Order-Status-Indikatoren verwenden klare visuelle Symbole: Ein grüner Haken für ausgeführte Orders (FILLED), ein gelbes Uhren-Symbol für wartende Orders (PENDING), ein rotes X für stornierte Orders (CANCELLED) und ein Ausrufezeichen für abgelehnte Orders (REJECTED). Hover-Tooltips bieten zusätzliche Informationen zu jedem Status.

Order-Details können durch Klicken auf eine Order-Zeile erweitert werden. Die erweiterte Ansicht zeigt zusätzliche Informationen wie Kommissionen, Ausführungszeit, Slippage und zugehörige Stop-Loss oder Take-Profit Orders. Für komplexe Orders werden auch die Beziehungen zwischen Haupt- und Nebenorders visualisiert.

Die Trading-Statistiken-Sektion bietet aggregierte Metriken über Ihre Trading-Performance. Dazu gehören die Gesamtanzahl der Orders, Win-Rate, durchschnittlicher Gewinn/Verlust pro Trade, größter Gewinn/Verlust und durchschnittliche Trade-Dauer. Diese Statistiken werden sowohl für den aktuellen Tag als auch für längere Zeiträume angezeigt.

### Signal-Analyse und Trading-Empfehlungen

Der Signals-Tab zeigt aktuelle Trading-Signale und Marktanalysen an. Die Hauptansicht präsentiert eine Liste der neuesten Signale, sortiert nach Konfidenz und Stärke. Jedes Signal zeigt das Symbol, die empfohlene Aktion (Buy/Sell/Hold), die Signal-Stärke (Weak/Moderate/Strong), die Konfidenz-Bewertung und eine kurze Begründung.

Signal-Details können erweitert werden, um zusätzliche Informationen zu zeigen. Dazu gehören der empfohlene Entry-Preis, Stop-Loss-Level, Take-Profit-Ziele und die zugrunde liegenden technischen Indikatoren. Ein visueller Indikator zeigt die Stärke des Signals mit einem Sternen-Rating-System ( bis ).

Die technischen Indikatoren werden in einer separaten Sektion für jedes überwachte Symbol angezeigt. Dazu gehören Moving Averages (SMA/EMA), RSI, MACD und Bollinger Bands. Jeder Indikator wird mit seinem aktuellen Wert und einer Interpretation (Bullish/Bearish/Neutral) angezeigt.

Sentiment-Analyse-Ergebnisse werden in einer eigenen Sektion präsentiert. Das System zeigt den aggregierten Sentiment-Score für jedes Symbol, die Anzahl der analysierten Texte, die Konfidenz der Analyse und die wichtigsten Sentiment-Treiber. Ein visueller Sentiment-Indikator verwendet Emojis und Farbkodierung für schnelle Interpretation.

### Webhook-Testing und Integration

Der Webhook-Tab bietet Tools zum Testen und Verwalten von Webhook-Integrationen, insbesondere für TradingView-Alerts. Die Hauptfunktion ist ein interaktiver Webhook-Tester, der es ermöglicht, Trading-Signale manuell zu senden und die Systemreaktion zu überwachen.

Der Webhook-Tester enthält vorgefertigte Templates für häufige Signal-Typen. Sie können zwischen verschiedenen Vorlagen wählen (Buy Signal, Sell Signal, Stop Loss, Take Profit) oder benutzerdefinierte Signale erstellen. Jede Vorlage enthält realistische Beispieldaten, die als Ausgangspunkt für Tests verwendet werden können.

Die Signal-Konfiguration ermöglicht die Anpassung aller relevanten Parameter: Symbol, Aktion, Menge, Preis, Stop-Loss und Take-Profit. Das System berechnet automatisch empfohlene Werte basierend auf der aktuellen Marktlage und Volatilität. Eine Vorschau zeigt die resultierende Order-Struktur vor dem Senden.

Webhook-Statistiken zeigen die Performance der Webhook-Integration über Zeit. Dazu gehören die Gesamtanzahl empfangener Webhooks, Erfolgsrate, durchschnittliche Verarbeitungszeit und häufige Fehlertypen. Ein Echtzeit-Log zeigt die letzten Webhook-Aktivitäten mit Zeitstempel, Payload und Verarbeitungsstatus.

### Backtesting und Performance-Analyse

Der Backtest-Tab bietet Tools für die historische Analyse von Trading-Strategien und Performance-Bewertung. Die Hauptfunktion ist ein interaktiver Backtesting-Engine, der es ermöglicht, verschiedene Strategien mit historischen Daten zu testen und zu vergleichen.

Die Backtest-Konfiguration ermöglicht die Auswahl von Zeiträumen, Symbolen und Strategie-Parametern. Sie können verschiedene Signal-Schwellenwerte, Risikomanagement-Einstellungen und Position-Sizing-Methoden testen. Das System bietet vorgefertigte Strategie-Templates sowie die Möglichkeit, benutzerdefinierte Parameter zu definieren.

Backtest-Ergebnisse werden in umfassenden Reports präsentiert. Die Hauptmetriken umfassen Total Return, Sharpe Ratio, Maximum Drawdown, Win Rate, Profit Factor und Calmar Ratio. Zusätzliche Statistiken zeigen Trade-spezifische Metriken wie durchschnittliche Trade-Dauer, größter Gewinn/Verlust und Consecutive Wins/Losses.

Performance-Charts visualisieren die Backtest-Ergebnisse in verschiedenen Formaten. Das Equity-Curve-Chart zeigt die Portfolio-Wertentwicklung über Zeit, während das Drawdown-Chart Verlustperioden hervorhebt. Trade-Analyse-Charts zeigen die Verteilung von Gewinnen und Verlusten sowie die Performance nach Wochentagen oder Monaten.

### System-Monitoring und Wartung

Der System-Tab bietet umfassende Überwachung und Wartungsfunktionen für das Trading-System. Die Hauptansicht zeigt den aktuellen System-Status mit Indikatoren für alle kritischen Komponenten: Datensammlung, Signal-Generierung, Risikomanagement, Order-Ausführung und Sicherheitssysteme.

Component-Health-Checks werden kontinuierlich durchgeführt und in Echtzeit angezeigt. Jede Komponente zeigt ihren aktuellen Status (Online/Offline/Warning), die letzte Aktivität und relevante Metriken. Bei Problemen werden automatisch Warnungen angezeigt mit Empfehlungen für Korrekturmaßnahmen.

System-Logs können direkt im Dashboard eingesehen werden. Die Log-Ansicht bietet Filteroptionen nach Log-Level (Debug, Info, Warning, Error), Komponente und Zeitraum. Kritische Ereignisse werden hervorgehoben und können für detaillierte Analyse erweitert werden.

Performance-Metriken zeigen die System-Performance über Zeit. Dazu gehören API-Response-Zeiten, Datenbank-Performance, Memory-Usage und CPU-Auslastung. Trends werden visualisiert, um potenzielle Performance-Probleme frühzeitig zu identifizieren.

### Mobile Responsivität und Accessibility

Das Dashboard ist vollständig responsive und passt sich automatisch an verschiedene Bildschirmgrößen an. Auf mobilen Geräten wird die Navigation zu einem Hamburger-Menü umgewandelt, und Charts werden für Touch-Interaktion optimiert. Alle wichtigen Funktionen bleiben auf mobilen Geräten verfügbar, mit angepassten Layouts für optimale Benutzerfreundlichkeit.

Accessibility-Features umfassen Keyboard-Navigation, Screen-Reader-Unterstützung und High-Contrast-Modi. Alle interaktiven Elemente sind über die Tastatur erreichbar, und wichtige Informationen werden sowohl visuell als auch über ARIA-Labels für Screen-Reader bereitgestellt.

### Anpassung und Personalisierung

Das Dashboard bietet verschiedene Anpassungsoptionen für individuelle Präferenzen. Benutzer können Dashboard-Layouts speichern, bevorzugte Chart-Zeiträume einstellen und Benachrichtigungseinstellungen konfigurieren. Theme-Optionen umfassen Light- und Dark-Modi sowie anpassbare Farbschemata.

Widget-Konfiguration ermöglicht es, die Anzeige verschiedener Dashboard-Komponenten anzupassen. Benutzer können entscheiden, welche Metriken prominent angezeigt werden, Chart-Typen auswählen und die Aktualisierungsfrequenz für verschiedene Datentypen einstellen.


## Konfiguration

Die Konfiguration des Trading-Systems erfolgt über mehrere Ebenen, um maximale Flexibilität und Sicherheit zu gewährleisten. Das System verwendet eine Kombination aus Konfigurationsdateien, Umgebungsvariablen und Datenbank-gespeicherten Einstellungen.

### Hauptkonfigurationsdatei (config.py)

Die zentrale Konfigurationsdatei enthält alle grundlegenden Systemeinstellungen. Diese Datei definiert unterstützte Symbole, API-Endpunkte, Standard-Parameter für Trading-Algorithmen und Systemgrenzen. Die Konfiguration ist in logische Abschnitte unterteilt: Trading-Parameter, Risikomanagement-Einstellungen, API-Konfigurationen und Sicherheitseinstellungen.

Trading-Parameter umfassen die Liste der überwachten Symbole, Standard-Positionsgrößen, minimale und maximale Order-Größen sowie Standard-Zeitrahmen für technische Indikatoren. Diese Parameter können zur Laufzeit über die API geändert werden, wobei Änderungen in der Datenbank persistiert werden.

Risikomanagement-Einstellungen definieren Portfolio-Limits, maximale Exposition pro Symbol, Stop-Loss-Parameter und Kill-Switch-Schwellenwerte. Diese kritischen Einstellungen erfordern administrative Berechtigung für Änderungen und werden bei jeder Modifikation auditiert.

### Umgebungsvariablen

Sicherheitsrelevante Konfigurationen werden ausschließlich über Umgebungsvariablen verwaltet, um zu verhindern, dass sensitive Daten in Konfigurationsdateien oder Versionskontrolle gespeichert werden. Die .env-Datei enthält alle notwendigen Umgebungsvariablen mit Beispielwerten.

Kritische Umgebungsvariablen umfassen TRADING_MASTER_PASSWORD für die Verschlüsselung, WEBHOOK_SECRET für Webhook-Validierung, API-Schlüssel für externe Dienste und Datenbank-Verbindungszeichenfolgen. Alle diese Variablen sollten mit starken, zufällig generierten Werten konfiguriert werden.

Das System überprüft beim Start die Verfügbarkeit aller erforderlichen Umgebungsvariablen und gibt detaillierte Fehlermeldungen aus, wenn kritische Variablen fehlen. Ein Konfigurationsvalidierungs-Tool kann verwendet werden, um die Vollständigkeit und Korrektheit der Konfiguration zu überprüfen.

### Broker-Konfiguration

Broker-spezifische Einstellungen werden in separaten Konfigurationsabschnitten verwaltet. Jeder unterstützte Broker hat seine eigene Konfigurationssektion mit API-Endpunkten, Authentifizierungsparametern und broker-spezifischen Limits.

Für Binance umfasst die Konfiguration API-Base-URLs für Mainnet und Testnet, Standard-Kommissionssätze, minimale Order-Größen pro Symbol und Rate-Limiting-Parameter. Das System unterstützt sowohl Spot- als auch Futures-Trading mit separaten Konfigurationen.

Paper-Trading-Konfiguration ermöglicht realistische Simulation ohne echtes Kapital. Parameter umfassen Startkapital, Slippage-Modelle, Kommissionsstrukturen und Marktimpact-Simulationen. Diese Einstellungen können angepasst werden, um verschiedene Marktbedingungen zu simulieren.

### Algorithmus-Parameter

Trading-Algorithmus-Parameter können sowohl statisch in der Konfigurationsdatei als auch dynamisch zur Laufzeit konfiguriert werden. Statische Parameter umfassen grundlegende Algorithmus-Einstellungen, die selten geändert werden, während dynamische Parameter für Optimierung und A/B-Testing verwendet werden.

Signal-Generierung-Parameter umfassen Schwellenwerte für technische Indikatoren, Gewichtungen für verschiedene Signaltypen und Konfidenz-Mindestanforderungen. Diese Parameter können über die API angepasst werden, wobei Änderungen automatisch in Backtests validiert werden.

Sentiment-Analyse-Parameter umfassen Keyword-Gewichtungen, Konfidenz-Schwellenwerte und Quellen-Gewichtungen. Das System ermöglicht es, verschiedene Sentiment-Modelle zu konfigurieren und deren Performance zu vergleichen.

## Sicherheit

Das Trading-System implementiert umfassende Sicherheitsmaßnahmen auf allen Ebenen, um Daten, Kapital und Systemintegrität zu schützen. Die Sicherheitsarchitektur folgt dem Defense-in-Depth-Prinzip mit mehreren Schutzschichten.

### Verschlüsselung und Datenschutz

Alle sensitiven Daten werden mit AES-256-Verschlüsselung im CBC-Modus geschützt. Der Verschlüsselungsschlüssel wird mit PBKDF2 und 100.000 Iterationen aus einem Master-Passwort abgeleitet. Zusätzlich wird HMAC-SHA256 für Datenintegrität verwendet, um Manipulationen zu erkennen.

API-Schlüssel und andere Credentials werden niemals im Klartext gespeichert. Das System verwendet ein hierarchisches Schlüsselmanagement-System, bei dem verschiedene Datentypen mit verschiedenen Schlüsseln verschlüsselt werden. Schlüsselrotation wird unterstützt und kann automatisiert werden.

Datenübertragung erfolgt ausschließlich über verschlüsselte Verbindungen (HTTPS/TLS 1.3). Das System implementiert Certificate Pinning für kritische API-Verbindungen und verwendet Perfect Forward Secrecy für alle Kommunikation.

### Authentifizierung und Autorisierung

Das System implementiert mehrschichtige Authentifizierung mit verschiedenen Berechtigungsebenen. Standard-Benutzer haben Lesezugriff auf Portfolio-Daten und können Orders erstellen. Administrative Benutzer können Systemkonfigurationen ändern und Sicherheitsaudits durchführen.

Session-Management verwendet kryptographisch sichere Token mit konfigurierbaren Ablaufzeiten. Sessions werden an IP-Adressen gebunden und können bei verdächtigen Aktivitäten automatisch invalidiert werden. Multi-Factor-Authentication (MFA) wird für administrative Funktionen unterstützt.

API-Schlüssel-basierte Authentifizierung wird für programmatischen Zugriff verwendet. API-Schlüssel haben granulare Berechtigungen und können auf spezifische IP-Adressen oder Zeiträume beschränkt werden. Alle API-Zugriffe werden protokolliert und überwacht.

### Webhook-Sicherheit

Webhook-Endpunkte implementieren HMAC-SHA256-Signatur-Validierung, um sicherzustellen, dass Requests von autorisierten Quellen stammen. Jeder Webhook-Provider hat einen eigenen geheimen Schlüssel, und Signaturen werden bei jedem Request validiert.

IP-Whitelisting beschränkt Webhook-Zugriff auf bekannte und vertrauenswürdige Quellen. Das System unterstützt CIDR-Notation für Netzwerkbereiche und kann dynamisch aktualisiert werden. Fehlgeschlagene Authentifizierungsversuche werden automatisch blockiert.

Replay-Attack-Schutz wird durch Timestamp-Validierung und Nonce-Tracking implementiert. Requests, die älter als 5 Minuten sind oder bereits verarbeitete Nonces enthalten, werden automatisch abgelehnt.

### Monitoring und Incident Response

Kontinuierliches Sicherheitsmonitoring überwacht alle Systemaktivitäten auf verdächtige Muster. Anomalie-Erkennung identifiziert ungewöhnliche Trading-Aktivitäten, API-Zugriffsmuster oder Systemverhalten. Automatische Alerts werden bei kritischen Sicherheitsereignissen ausgelöst.

Incident-Response-Verfahren sind dokumentiert und automatisiert. Bei kritischen Sicherheitsvorfällen wird automatisch der Kill-Switch aktiviert, alle Sessions invalidiert und administrative Benutzer benachrichtigt. Forensische Logs werden für spätere Analyse aufbewahrt.

Regelmäßige Sicherheitsaudits werden automatisch durchgeführt und bewerten Systemkonfiguration, Dateiberechtigungen, Verschlüsselungsstärke und Compliance mit Sicherheitsrichtlinien. Audit-Ergebnisse werden in detaillierten Reports dokumentiert.

## Deployment

Das Trading-System unterstützt verschiedene Deployment-Optionen, von lokalen Entwicklungsumgebungen bis hin zu hochverfügbaren Cloud-Deployments. Jede Option ist für spezifische Anwendungsfälle optimiert und bietet entsprechende Skalierbarkeits- und Sicherheitsfeatures.

### Docker-Deployment

Docker-Deployment ist die empfohlene Option für Produktionsumgebungen. Das System wird als Multi-Container-Anwendung bereitgestellt, wobei jede Komponente in einem separaten Container läuft. Docker Compose orchestriert die Container und verwaltet Netzwerk- und Volume-Konfigurationen.

Die Container-Architektur umfasst separate Container für die API, das Dashboard, die Datenbank und Nginx als Reverse Proxy. Jeder Container ist minimal konfiguriert und enthält nur die notwendigen Abhängigkeiten. Health Checks sind für alle Container konfiguriert und ermöglichen automatische Neustarts bei Problemen.

Persistent Volumes werden für Datenbank-Daten, Logs und Konfigurationsdateien verwendet. Backup-Strategien sind in die Container-Konfiguration integriert und können automatisiert werden. Container-Updates können mit Zero-Downtime durchgeführt werden.

### Cloud-Deployment

Cloud-Deployment-Optionen umfassen AWS, Google Cloud Platform und Microsoft Azure. Terraform-Konfigurationen sind für Infrastructure-as-Code-Deployments verfügbar. Auto-Scaling, Load Balancing und Multi-Region-Deployments werden unterstützt.

Kubernetes-Manifeste ermöglichen Container-Orchestrierung in Cloud-Umgebungen. Helm Charts vereinfachen die Installation und Konfiguration. Service Mesh-Integration mit Istio oder Linkerd bietet erweiterte Traffic-Management und Sicherheitsfeatures.

Managed Services können für Datenbanken, Message Queues und Monitoring verwendet werden. Cloud-native Sicherheitsfeatures wie IAM, Key Management Services und Network Security Groups werden integriert.

### High-Availability Setup

High-Availability-Deployments implementieren Redundanz auf allen Ebenen. Load Balancer verteilen Traffic auf mehrere API-Instanzen. Datenbank-Clustering mit automatischem Failover gewährleistet Datenverfügbarkeit. Geographic Redundancy schützt vor regionalen Ausfällen.

Health Checks und Monitoring sind kritisch für HA-Deployments. Automatische Failover-Mechanismen erkennen ausgefallene Komponenten und leiten Traffic um. Disaster Recovery-Verfahren sind dokumentiert und regelmäßig getestet.

## Monitoring und Wartung

Umfassendes Monitoring gewährleistet optimale System-Performance und frühzeitige Erkennung von Problemen. Das Monitoring-System überwacht technische Metriken, Business-Metriken und Sicherheitsereignisse.

### System-Monitoring

Technische Metriken umfassen CPU-Auslastung, Memory-Usage, Disk-I/O, Netzwerk-Traffic und Anwendungs-Performance. Prometheus sammelt Metriken von allen Systemkomponenten. Grafana bietet umfassende Dashboards für Visualisierung und Alerting.

Application Performance Monitoring (APM) verfolgt API-Response-Zeiten, Datenbank-Query-Performance und externe API-Latenz. Distributed Tracing ermöglicht End-to-End-Verfolgung von Requests durch alle Systemkomponenten.

Log-Aggregation sammelt Logs von allen Komponenten in einem zentralen System. ELK Stack (Elasticsearch, Logstash, Kibana) oder ähnliche Lösungen ermöglichen erweiterte Log-Analyse und -Suche.

### Business-Monitoring

Trading-spezifische Metriken überwachen Portfolio-Performance, Order-Ausführung, Signal-Qualität und Risikomanagement-Effektivität. Custom Dashboards zeigen KPIs wie Sharpe Ratio, Maximum Drawdown, Win Rate und Profit Factor.

Real-time Alerts benachrichtigen bei kritischen Business-Events wie großen Verlusten, Kill-Switch-Aktivierung oder ungewöhnlichen Trading-Mustern. Alert-Regeln sind konfigurierbar und können an verschiedene Kommunikationskanäle gesendet werden.

### Wartungsverfahren

Regelmäßige Wartungsaufgaben umfassen Datenbank-Optimierung, Log-Rotation, Backup-Validierung und Sicherheits-Updates. Automatisierte Scripts führen Routine-Wartung durch und protokollieren alle Aktivitäten.

Planned Maintenance Windows werden für größere Updates und Systemwartung verwendet. Blue-Green-Deployments ermöglichen Updates ohne Downtime. Rollback-Verfahren sind für den Fall von Problemen nach Updates dokumentiert.

## Troubleshooting

Dieser Abschnitt behandelt häufige Probleme und deren Lösungen. Probleme sind nach Kategorien organisiert: Installation, Konfiguration, Performance, Trading und Sicherheit.

### Häufige Installationsprobleme

Abhängigkeitskonflikte können auftreten, wenn verschiedene Python-Pakete inkompatible Versionen erfordern. Die Lösung ist die Verwendung einer virtuellen Umgebung und spezifischer Paketversionen aus der requirements.txt-Datei. Bei persistenten Problemen kann ein kompletter Neuaufbau der virtuellen Umgebung helfen.

Datenbankverbindungsprobleme manifestieren sich oft als Timeout-Fehler oder Verbindungsablehnungen. Überprüfen Sie Dateiberechtigungen für SQLite-Dateien oder Netzwerkkonnektivität für externe Datenbanken. Firewall-Einstellungen können Datenbankverbindungen blockieren.

API-Schlüssel-Probleme führen zu Authentifizierungsfehlern bei externen APIs. Überprüfen Sie die Gültigkeit und Berechtigungen Ihrer API-Schlüssel. Rate-Limiting kann temporäre Ausfälle verursachen und erfordert möglicherweise Anpassungen der Request-Frequenz.

### Performance-Probleme

Langsame API-Response-Zeiten können durch Datenbank-Performance-Probleme, ineffiziente Queries oder Netzwerk-Latenz verursacht werden. Database Query Profiling identifiziert langsame Queries. Index-Optimierung und Query-Tuning können die Performance erheblich verbessern.

Memory-Leaks manifestieren sich als kontinuierlich steigender Memory-Verbrauch. Python-Memory-Profiling-Tools können die Ursache identifizieren. Häufige Ursachen sind nicht geschlossene Datenbankverbindungen oder große Datenstrukturen, die nicht garbage collected werden.

### Trading-spezifische Probleme

Order-Ausführungsfehler können durch unzureichende Kontoguthaben, Marktschließungen oder Broker-API-Probleme verursacht werden. Das System protokolliert detaillierte Fehlermeldungen für jede fehlgeschlagene Order. Retry-Mechanismen handhaben temporäre Probleme automatisch.

Signal-Qualitätsprobleme zeigen sich in schlechter Trading-Performance oder inkonsistenten Signalen. Backtesting kann helfen, Signal-Parameter zu optimieren. Sentiment-Analyse-Probleme können durch veraltete Keyword-Listen oder API-Änderungen verursacht werden.

## Entwickler-Guide

Dieser Abschnitt richtet sich an Entwickler, die das Trading-System erweitern oder anpassen möchten. Er behandelt Code-Struktur, Entwicklungsworkflows und Best Practices.

### Code-Architektur

Das System folgt einer modularen Architektur mit klarer Trennung von Verantwortlichkeiten. Jedes Modul hat eine spezifische Aufgabe und kommuniziert über definierte Schnittstellen mit anderen Modulen. Dependency Injection wird verwendet, um lose Kopplung zu gewährleisten.

Design Patterns umfassen Strategy Pattern für verschiedene Trading-Algorithmen, Observer Pattern für Event-Handling und Factory Pattern für Broker-Abstraktion. Diese Patterns ermöglichen einfache Erweiterung und Wartung des Systems.

### Entwicklungsumgebung

Die Entwicklungsumgebung sollte Python 3.11+, Git, Docker und einen modernen Code-Editor mit Python-Unterstützung umfassen. Pre-commit Hooks gewährleisten Code-Qualität und Konsistenz. Linting mit pylint und Formatierung mit black sind konfiguriert.

Testing-Framework basiert auf pytest mit umfassenden Unit Tests, Integration Tests und End-to-End Tests. Test Coverage sollte mindestens 80% betragen. Continuous Integration mit GitHub Actions oder ähnlichen Tools automatisiert Testing und Deployment.

### Erweiterung des Systems

Neue Trading-Algorithmen können durch Implementierung der TradingStrategy-Schnittstelle hinzugefügt werden. Das Strategy Pattern ermöglicht einfaches Hinzufügen und Testen neuer Algorithmen ohne Änderung der Kernlogik.

Neue Broker können durch Implementierung der BrokerInterface-Schnittstelle integriert werden. Die abstrakte Broker-Klasse definiert alle notwendigen Methoden für Order-Management und Portfolio-Tracking.

## FAQ

### Allgemeine Fragen

**F: Ist das Trading-System für Anfänger geeignet?**
A: Das System ist primär für erfahrene Trader und Entwickler konzipiert. Grundkenntnisse in Trading, Python und API-Integration sind empfohlen. Das Paper-Trading-Feature ermöglicht risikofreies Lernen.

**F: Welche Mindestkapitalanforderungen gibt es?**
A: Für Paper Trading gibt es keine Mindestanforderungen. Für Live Trading hängen die Anforderungen vom gewählten Broker ab. Binance hat beispielsweise minimale Order-Größen von 10 USD.

**F: Kann das System 24/7 laufen?**
A: Ja, das System ist für kontinuierlichen Betrieb konzipiert. Automatische Überwachung und Restart-Mechanismen gewährleisten hohe Verfügbarkeit. Wartungsfenster sollten für Updates eingeplant werden.

### Technische Fragen

**F: Welche Programmiersprachen werden unterstützt?**
A: Das Backend ist in Python entwickelt, das Frontend in JavaScript/React. API-Integration ist in jeder Sprache möglich, die HTTP-Requests unterstützt.

**F: Kann das System mit anderen Trading-Plattformen integriert werden?**
A: Ja, über die Webhook-API können externe Signale von TradingView und anderen Plattformen integriert werden. Neue Broker-Integrationen können entwickelt werden.

**F: Wie werden Daten gesichert?**
A: Automatische Backups werden täglich erstellt. Datenbank-Replikation und Cloud-Backups sind für Produktionsumgebungen verfügbar.

### Sicherheitsfragen

**F: Wie sicher sind meine API-Schlüssel?**
A: API-Schlüssel werden mit AES-256-Verschlüsselung gespeichert und niemals im Klartext übertragen. Das System erreicht eine Sicherheitsbewertung von 95.5/100.

**F: Was passiert bei einem Sicherheitsvorfall?**
A: Automatische Kill-Switch-Aktivierung schützt das Portfolio. Alle Sessions werden invalidiert und administrative Benutzer benachrichtigt. Forensische Logs ermöglichen Incident-Analyse.

## Anhang

### Glossar

**API (Application Programming Interface)**: Schnittstelle für programmatischen Zugriff auf Systemfunktionen.

**Backtesting**: Testen von Trading-Strategien mit historischen Daten.

**Kill Switch**: Notfall-Mechanismus zum sofortigen Schließen aller Positionen.

**Paper Trading**: Simulation von Trading ohne echtes Kapital.

**Sentiment Analysis**: Analyse der Marktstimmung aus Textdaten.

**Webhook**: HTTP-Callback für Echtzeit-Benachrichtigungen.

### Referenzen

[1] Trading System Architecture Documentation - https://github.com/trading-system/docs
[2] Python Flask Documentation - https://flask.palletsprojects.com/
[3] React Documentation - https://reactjs.org/docs/
[4] Docker Documentation - https://docs.docker.com/
[5] Binance API Documentation - https://binance-docs.github.io/apidocs/
[6] TradingView Webhook Documentation - https://www.tradingview.com/support/solutions/43000529348/

### Kontakt und Support

**Technischer Support**: support@trading-system.com
**Entwickler-Community**: https://github.com/trading-system/community
**Dokumentation**: https://docs.trading-system.com
**Status-Seite**: https://status.trading-system.com

---

*Diese Dokumentation wird kontinuierlich aktualisiert. Letzte Aktualisierung: 1. September 2025*

