# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier dokumentiert.

Das Format orientiert sich an [Keep a Changelog](https://keepachangelog.com/de/1.1.0/),
die Versionierung folgt [Semantic Versioning](https://semver.org/lang/de/).

## [Unveröffentlicht]

## [0.1.0] – 2026-09-14

Erste versionierte Fassung. Sie fasst den bisherigen Entwicklungsstand zusammen: 12 Commits seit 2025-09-01.

### Behoben

- security - update vulnerable dependencies to safe versions
- clean up leading spaces in log strings after emoji removal

### Geändert

- remove AI-generated emojis from source and documentation Strip emojis from code comments, log statements and markdown headings across all source and documentation files. Reduces visual noise and removes obvious AI-generation markers.

### Dokumentation

- highlight KI sentiment analysis and security score 95.5/100 in README
- add professional README
- README neu strukturiert + 3 ADRs (Vanity-Metriken entfernt, Architektur-Diagramm + Entscheidungsdoku)

### Weitere Änderungen

- Revise README for clarity and added features
- Update contact email to tobias.buss.dev@gmail.com
- Add comprehensive test suite: unit, functional, regression tests (47 tests passing); fix syntax errors in risk_manager.py

[Unveröffentlicht]: https://github.com/tib019/automated-trading-system/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tib019/automated-trading-system/releases/tag/v0.1.0
