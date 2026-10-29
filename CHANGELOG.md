# Changelog

Änderungen am Repo als Ganzem. Managr hat eine eigene Version; die Vorgeschichte des Beute-Teils steht in
[CHANGELOG-beute.md](mods/managr/CHANGELOG-beute.md).

## [Unreleased]

## [3.1.0] - 2026-10-29

### Hinzugefügt
- **Managr 1.2.0**: `/sichern <x z> <Radius>` sichert vor einem Geländeumbau die betroffenen Regionsdateien (region, entities, poi) nach `sicherungen/<Zeitpunkt>/`.
- **Managr 1.2.0**: Explosionsschutz im Spawnschutz-Bereich (`protect_blocks_from_explosions`, Standard aus): Explosionen zerstören und entzünden dort keine Blöcke, Schaden und Rückstoß bleiben.

## [3.0.0] - 2026-10-28

### Geändert
- **Managr 1.1.0** für Minecraft 26.3 (Fabric Loader 0.20.1, Fabric API 0.165.0): `LootContext#getOptional` statt `getOptionalParameter`, `NaturalSpawner#spawnMobsForChunkGeneration` nimmt jetzt eine `BlockPos` statt des Bioms. Für 26.2 bleibt Managr 1.0.0.
- **Managr 1.0.0** fasst die reinen Server-Mods zusammen: Loot Scaler 1.0.2, Spawn Guard 1.1.0 (bisher eigener Ordner außerhalb des Repos) und Stumm 1.5.0. Paket `io.github.dschonas04.managr`, Konfigurationsdateien unverändert, die alten Jars werden per `breaks` ausgeschlossen.

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
