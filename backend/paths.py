"""Zentrale Pfadaufloesung fuer das Trading-System.

Bis hierher standen die Pfade als Literale ('/home/ubuntu/trading_system/...')
in 27 Dateien. Dadurch lief das System ausschliesslich auf der Maschine, auf
der es urspruenglich entwickelt wurde: Datenbank, Logdatei und Konfiguration
lagen auf jedem anderen Rechner an nicht existierenden Orten, was sich als
sqlite3.OperationalError beim Start und in der Testsuite aeusserte.

BASE_DIR ist per Umgebungsvariable TRADING_SYSTEM_HOME ueberschreibbar und
faellt sonst auf das Verzeichnis dieser Datei zurueck.
"""
import os

BASE_DIR = os.environ.get("TRADING_SYSTEM_HOME") or os.path.dirname(os.path.abspath(__file__))


def in_base(*parts: str) -> str:
    """Pfad relativ zu BASE_DIR zusammensetzen."""
    return os.path.join(BASE_DIR, *parts)
