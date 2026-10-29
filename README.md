# mc-serververwaltung

Werkzeuge zum Verwalten eines Minecraft-Servers (Fabric, Minecraft 1.21.11 – Zweig mc/1.21.11, gebaut mit Loom und Mojang-Mappings; aktuell ist main): eigene Server-Mods, Datenpakete und Skripte.

| Ordner | Inhalt |
|---|---|
| [`mods/managr`](mods/managr) | **Managr**: alle reinen Server-Mods in einer – Beute, Spawnschutz und Verwaltung (siehe unten) |
| [`datenpakete`](datenpakete) | Eigene Datenpakete der Welt |
| [`skripte`](skripte) | Allgemeine Werkzeuge: RCON, Chunky im Leerlauf, Telegram-Brücke, Welt-Scans, ChestLogger-Auswertung, Bau-Skripte mit Parametern |

## Managr

Eine Mod, nur Server, braucht Fabric API. Sie fasst seit 1.0.0 die früheren Einzel-Mods Loot Scaler, Spawn Guard und
Stumm zusammen; deren Jars müssen aus dem `mods`-Ordner raus (Managr verweigert sonst den Start). Die Konfigurationsdateien
bleiben dieselben.

### Beute (ex Loot Scaler)

Erze und Mobs geben weniger: Mengen und der Glück-Bonus werden skaliert, nie die Chance – ein einzelnes Erz bleibt ein Erz.
Einstellungen in `config/loot-scaler.properties` (`ores`, `mobs`, `never_zero`, `debug`). Ausführlich in
[README-beute.md](mods/managr/README-beute.md).

### Spawnschutz (ex Spawn Guard)

In einem Quadrat um einen Punkt (Standard: Weltspawn, Radius 10 Chunks) entstehen keine feindlichen Mobs – der Spawnversuch
fällt weg, nichts stirbt, keine Beute. Dazu die Mob-Dichte um die Spieler (`monster_cap`, `animal_cap`, `water_cap`,
`ambient_cap`) und wie oft Tiere spawnen dürfen (`animal_interval`). Einstellungen in `config/spawn-guard.properties`.

### Verwaltung (ex Stumm)

| Funktion | Befehl / Datei |
|---|---|
| Spieler stummschalten | `/stumm <Spieler>`, `/laut <Spieler>`, `/stumm liste` (Ops), Liste in `config/stumm.txt` |
| Spender | `/spende <Spieler> <Euro>`, `/spende setzen`, `/spende entfernen`, `/spende liste` (Ops), `/spender` für alle; Daten in `config/spender.txt` |
| Ehrentafel | schwebende Top-10-Spendertafel am Spawn (0.5 66.2 -8.5), Spender haben goldene Namen |
| Hexenhütte | `/hexenhuette <x y z>` (Ops) legt an beliebiger Stelle eine Sumpfhütten-Struktur ohne Blöcke an (7 × 7 × 9, kleinste Ecke an der Stelle); darin erscheinen Hexen wie in einer echten Hütte |
| Werkzeugwache | Log-Zeile `Werkzeugwache`, wenn einem Spieler ein Gegenstand mit Haltbarkeit aus dem Inventar verschwindet (Ort, Dimension, vermuteter Grund) |
| Tierwache | jedes von einem Spieler getötete Tier (alle Mobs außer Monstern) mit Täter, Ort und Besitzer ins Log und nach `logs/tiere.log`; benannte, gezähmte Tiere und Happy Ghasts auch ohne Spieler als Täter |
| Log-Filter | blendet die Spam-Meldung „Invalid entity rotation: NaN“ aus |

## Bauen

Minecraft 26.2 ist nicht verschleiert, Managr baut mit normalem Gradle direkt gegen das Server-Jar, ohne Loom.
Java 25 und Gradle nötig:

```bash
tools/fetch-libs.sh   # Server-Jar, gebündelte Bibliotheken und Fabric-API-Module nach libs/
gradle build          # Jars in mods/*/build/libs/
```

`libs/` ist nicht im Repo, das Minecraft-Jar darf nicht weitergegeben werden.
Ein Tag `v*` baut Managr und hängt die Jars an ein GitHub-Release.

## Lizenz

[MIT](LICENSE)
