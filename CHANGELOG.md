# Changelog

Änderungen am Repo als Ganzem. Die Mods haben eigene Versionen; Loot Scaler führt
zusätzlich [sein eigenes Changelog](mods/loot-scaler/CHANGELOG.md).

## [Unreleased]

### Hinzugefügt
- stumm 1.5.0: Tierwache protokolliert getötete Tiere mit Täter, Ort und Besitzer (Log und `logs/tiere.log`).

## [2.1.0] - 2026-10-14

### Geändert
- Skripte sind jetzt allgemein: gemeinsame Bibliothek `mcwerkzeug.py`, Server-Verzeichnis über `--server`/`MC_DIR`,
  RCON-Port und -Kennwort aus `server.properties`, keine festen Pfade, Namen oder Koordinaten mehr.
- Bau-Skripte mit Parametern statt fester Orte: Marktviertel, Verkaufsbude (Stil Zelt oder Nether, beliebige Ware und
  Preis), Hütte, Portalplatz, Teich, Weg, Begrünen, Ersetzen. Ausgabe als Datei, auf die Standardausgabe oder direkt
  per RCON, Chunks werden dafür automatisch geladen.
- `scan.py` (Höhenkarte, Bauwerke, kleine Wasserstellen) und `truhenlog.py` (ChestLogger) ersetzen die Einzelskripte.
- Telegram-Brücke: Name, Token, Zustandsordner über Umgebungsvariablen; Spielernamen werden nur mit Ranglisten-Präfix („1. “) und -Zusatz („12 Tode“) erkannt, damit /say und /me keine falschen Meldungen erzeugen.

### Behoben
- Der NBT-Leser las bei verschachtelten Einträgen den Wert vor dem Schlüssel.

## [2.0.0] - 2026-10-14

### Neu
- Aus `loot-scaler` wird `mc-serververwaltung`: Loot Scaler liegt jetzt unter `mods/loot-scaler`.
- Mod **Stumm 1.3.0** (`mods/stumm`): Stummschalten, Werkzeugwache, Log-Filter, Spender mit Ehrentafel und goldenen Namen.
- Eigene Datenpakete des Servers (`datenpakete/`).
- Skripte: RCON, Chunky im Leerlauf, Telegram-Brücke, Bau- und Analyseskripte (`skripte/`).
- Ein Tag `v*` baut beide Mods und hängt beide Jars ans Release.
