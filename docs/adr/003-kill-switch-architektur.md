# ADR-003: Kill-Switch als dedizierter Safety-Layer

**Status:** Accepted  
**Datum:** 2024

## Kontext

Automatisierte Handelssysteme müssen in der Lage sein, sich selbst abzuschalten, wenn Anomalien auftreten — z.B. übermäßige Verluste, API-Ausfälle, Datenfehler oder unerwartetes Systemverhalten.

Die naheliegende Lösung: `try/except`-Blöcke im Signal Generator und Order Manager, die bei Fehlern den Prozess stoppen.

## Entscheidung

Wir implementieren einen **dedizierten Kill-Switch als separates Modul** (`kill_switch.py`) mit eigenem State, das zwischen allen anderen Modulen als Gatekeeper sitzt.

```
Signal Generator → Risk Manager → [KILL SWITCH GATE] → Order Manager
```

Der Kill Switch hält seinen eigenen Zustand (`ACTIVE` / `TRIGGERED`) persistent, prüft mehrere Bedingungen unabhängig voneinander und lässt sich manuell zurücksetzen:

```python
# kill_switch.py
class KillSwitch:
    def check_conditions(self) -> bool:
        return all([
            self._check_daily_loss_limit(),
            self._check_consecutive_losses(),
            self._check_api_health(),
            self._check_drawdown(),
        ])

    def trigger(self, reason: str):
        self.state = 'TRIGGERED'
        self._log_trigger(reason)
        self._notify_dashboard()
```

## Warum nicht verteilte Error-Behandlung?

Jedes Modul mit `try/except` zu versehen hat ein fundamentales Problem: **kein gemeinsamer Zustand**. Modul A weiß nicht, dass Modul B bereits einen Fehler abgefangen hat. Bei einem Drawdown-Limit werden möglicherweise trotzdem noch Orders platziert, weil die Order-Logik den Kontext nicht kennt.

Ein zentraler Kill Switch ist der einzige Weg, eine globale `HALT`-Entscheidung atomar und konsistent zu erzwingen.

## Konsequenzen

**Positiv:**
- Single Source of Truth für den System-Status
- Dashboard kann Kill-Switch-State direkt anzeigen und manuell steuern
- Erweiterbar: neue Bedingungen werden nur im Kill Switch ergänzt, nicht in jedem Modul
- Fail-safe by default: bei Unsicherheit stoppt das System

**Negativ:**
- Zentraler Single Point of Failure: wenn der Kill Switch selbst crasht, gibt es kein Fallback
- Manuelles Reset erforderlich nach Trigger — das System startet nicht automatisch neu (bewusste Entscheidung)
