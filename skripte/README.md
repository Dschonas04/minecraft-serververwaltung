# Skripte

Allgemeine Werkzeuge für einen Minecraft-Server (Python 3, keine Zusatzpakete). Alle laufen auf dem Server selbst.

**Server-Verzeichnis:** `--server PFAD`, sonst Umgebungsvariable `MC_DIR`, sonst das aktuelle Verzeichnis.
**RCON:** Kennwort und Port liest jedes Skript aus `server.properties` (`enable-rcon=true`), nie aus der Befehlszeile.
`mcwerkzeug.py` enthält die gemeinsamen Bausteine (RCON, Regionsdateien lesen, Bauten ausgeben).

## Server

| Skript | Zweck |
|---|---|
| `rcon.py list` | Befehle schicken; `-f datei` bzw. `-f -` liest Befehlszeilen (`sleep N`, `#`-Kommentare) |
| `chunky-leerlauf.py` | Chunky-Vorgenerierung nur, solange die Tickzeit es erlaubt; mit `chunky-leerlauf.service/.timer` alle 30 s |
| `telegram-bruecke/` | Chat-Brücke Server ⇄ Telegram-Gruppe; Einstellungen in `mc-telegram.env` (Vorlage `.env.example`) |

## Welt lesen

| Skript | Zweck |
|---|---|
| `scan.py hoehen --mitte "x z" --radius R` | Höhenkarte, `~` = Wasser |
| `scan.py gebaut --mitte "x z" --radius R` | Blöcke, die nach Bauwerk aussehen, mit Fläche: vor jedem Geländeumbau prüfen |
| `scan.py wasser --mitte "x z" --radius R [--fuellen]` | kleine, abgeschlossene Wasserstellen finden und zuschütten |
| `truhenlog.py --besitzer A,B [--seit JJJJ-MM-TT]` | Mod ChestLogger: wer hat aus wessen Kisten etwas genommen |

## Bauen

Alle Bau-Skripte schreiben Befehle auf die Standardausgabe, mit `-o datei` in eine Datei oder schicken sie mit
`--senden` direkt an den Server. Die nötigen Chunks werden dabei per `forceload` geladen und wieder freigegeben.
**Vorher die betroffenen Regionsdateien sichern** und mit `scan.py gebaut` prüfen, dass dort nichts steht.

| Skript | Baut |
|---|---|
| `bau/marktviertel.py --ort "x y z" --staende 5` | Straße mit Marktständen (Fass-Theken, Markisen), Brunnen, Laternen |
| `bau/verkaufsbude.py --ort "x y z" --stil zelt\|nether --ware … --preis "minecraft:diamond 2"` | große Bude mit Händler, Leuchtrahmen, Schildern |
| `bau/huette.py --ort "x y z" --besitzer Name` | Fichtenhütte mit Einrichtung |
| `bau/portalplatz.py --mitte "x y z" [--aerialhell]` | runder Platz mit entzündetem Nether-Portal (und Aerial-Hell-Portal) |
| `bau/teich.py --mitte "x y z" --rx 12 --rz 8` | natürlicher Teich mit Ufer und Pflanzen |
| `bau/weg.py --von "x z" --bis "x z" --hoehe y` | Trampelpfad mit Laternen |
| `bau/begruenen.py --mitte "x y z" --radius R --baeume N --blumen N --frei "x1 z1 x2 z2"` | Bäume und Blumen, Sperrflächen ausgespart |
| `bau/pulvermuehle.py --mitte "x y z"` | Schwarzpulver-Mühle mit Create: Wasserrad, Mixer (32 U/min), Becken, Ein- und Ausgabekiste (2 Kohle + 1 Lohenstaub = 3 Schwarzpulver) |
| `bau/ersetzen.py --mitte "x z" --radius R --tausch alt=neu` | Blöcke im Gebiet austauschen |

Beispiel:

```bash
export MC_DIR=/srv/minecraft
python3 scan.py gebaut --mitte "-30 0" --radius 25
python3 bau/marktviertel.py --ort "-10 62 0" --staende 3 -o markt.txt   # ansehen ...
python3 rcon.py -f markt.txt                                              # ... und bauen
```
