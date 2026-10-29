# Managr – Ideen zum Erweitern

Vorschläge, noch nicht umgesetzt. Jede Idee passt in einen der drei Teile (Beute, Spawnschutz, Verwaltung) oder
bekommt einen eigenen Unterordner. Nur Server-Seite, keine Client-Mod nötig.

## Verwaltung

| Idee | Befehl / Datei | Nutzen |
|---|---|---|
| Grundstücke | `/grund setzen <x1 z1 x2 z2>`, `/grund freigeben <Spieler>`, `config/grundstuecke.txt` | Abbauen, Bauen und Kisten öffnen nur für Besitzer und Freigegebene; schützt Häuser wie die am Spawn-Markt |
| Kistenschutz | `/sperren`, `/entsperren` auf die angeschaute Kiste | leichter als Grundstücke, ersetzt das Nachlesen mit ChestLogger |
| Kistenprotokoll eingebaut | `logs/kisten.log`, `/kisten <x y z>` (Ops) | wer hat was aus welcher Kiste genommen, ohne Fremd-Mod; `truhenlog.py` liest dann diese Datei |
| Blockprotokoll | `logs/bloecke.log`, `/wer <x y z>` (Ops) | wer hat einen Block abgebaut oder gesetzt (Grief-Aufklärung, kurz: wie CoreProtect light) |
| Verwarnungen | `/verwarnen <Spieler> <Grund>`, `/verwarnungen <Spieler>`, `config/verwarnungen.txt` | Verlauf statt Erinnerung; ab N Verwarnungen automatisch stumm |
| Zeitlich stumm | `/stumm <Spieler> 30m` | Stummschaltung läuft von selbst ab |
| Chatfilter | `config/chatfilter.txt` (ein Wort/Regex je Zeile) | Wörter ersetzen oder Nachricht verwerfen, Treffer ins Log |
| Spielzeit | `/spielzeit [Spieler]`, Top-10 wie die Ehrentafel | Statistik aus den Vanilla-Stats, ohne Datenbank |
| AFK-Erkennung | `config/afk.properties` (`minuten`, `kicken`) | AFK-Spieler im Tab markieren, optional nach X Minuten kicken, wenn der Server voll ist |
| Begrüßung + Regeln | `config/willkommen.txt`, `/regeln` | Text beim ersten Beitritt und auf Abruf |
| Ankündigungen | `config/ankuendigungen.txt`, Intervall in Minuten | wiederkehrende Hinweise (Discord/Telegram, Spenden, Regeln) |
| Wartungsmodus | `/wartung an|aus` | nur Ops dürfen rein, alle anderen sehen eine Meldung im Serverbrowser (MOTD) |
| Neustart-Countdown | `/neustart 5m` | Warnung im Chat (5 min, 1 min, 10 s), dann `stop`; passt zum AMP-Neustart |
| Spender-Extras | `config/spender.properties` | Rang-Präfix im Chat ab Betrag X, Partikel an der Ehrentafel, Dankesnachricht beim Beitritt |

## Welt und Sicherheit

| Idee | Befehl / Datei | Nutzen |
|---|---|---|
| Sicherung vor Umbau | `/sichern <x z> <radius>` (Ops) | kopiert die betroffenen `.mca`-Dateien nach `sicherungen/<datum>/` – Lehre aus dem Berg-Absenken am 08.10. |
| Explosionsschutz | `config/explosionen.properties` (`spawn_radius`, `creeper`, `tnt`) | keine Blockschäden durch Creeper/TNT im Spawnbereich, Rest der Welt bleibt wie er ist; wichtig mit TNT Arsenal |
| TNT-Freigabe | `/tnt erlauben <Spieler>` | nur freigegebene Spieler dürfen TNT-Arsenal-Sprengstoff zünden |
| Feuer am Spawn | in `spawn-guard.properties`: `feuer=false` | kein Feuerausbreiten und kein Blitzfeuer im Schutzbereich |
| Endermen-Griefing | `enderman_bloecke=false` | Endermen nehmen keine Blöcke mehr, ohne `mobGriefing` global abzuschalten |
| Weltgrenze je Dimension | `config/grenzen.properties` | Nether/End kleiner halten als die Oberwelt |

## Beute und Spawnschutz

| Idee | Datei | Nutzen |
|---|---|---|
| Faktor je Erz/Mob | `loot-scaler.properties`: `ore.minecraft:diamond_ore=0.5` | einzelne Erze oder Mobs anders skalieren als den Rest |
| Faktor je Dimension | `nether.ores`, `end.mobs` | Nether-Erze knapper, Oberwelt normal |
| Mob-Farm-Bremse | `farm_limit` je Chunk und Stunde | Beute sinkt, wenn in einem Chunk sehr viele Mobs sterben; Farmen gehen, fluten aber nicht die Wirtschaft |
| Mehrere Schutzzonen | `spawn-guard.properties`: `zone.markt=-47 -12 -11 12` | neben dem Spawn auch Markt, Dorf usw. mobfrei |
| Tagsüber-Phantome aus | `phantome=false` oder `phantome_nach_tagen=10` | Phantome erst nach X Tagen ohne Schlaf, oder gar nicht |

## Wirtschaft

| Idee | Befehl / Datei | Nutzen |
|---|---|---|
| Vertrauenskasse digital | Schild `[Kasse]` an Kiste | Kiste nimmt nur einen festgelegten Preis entgegen und gibt die Ware heraus; Einnahmen in eine Besitzerkiste |
| Marktübersicht | `/markt` | listet alle Kassen mit Ware, Preis, Bestand und Ort |
| Händler-Log | `logs/markt.log` | jeder Kauf mit Käufer, Ware, Preis |

## Anbindung

| Idee | Datei | Nutzen |
|---|---|---|
| Telegram direkt | `config/telegram.properties` | Chat-Brücke in der Mod statt als eigener Dienst (`skripte/telegram-bruecke`), plus Meldungen bei Beitritt, Tod, Verwarnung |
| Prometheus-Exporter | `config/metriken.properties` (`port=9940`) | Spieler online, TPS, MSPT, geladene Chunks, Entitäten je Dimension → Grafana auf 10.0.2.43:3030 |
| Webhook bei Ereignissen | `config/webhook.properties` | Verwarnung, Grief-Verdacht, Werkzeugwache-Treffer an n8n schicken |

## Reihenfolge (Vorschlag)

1. Sicherung vor Umbau, Explosionsschutz am Spawn – schützt, was schon gebaut ist.
2. Grundstücke oder Kistenschutz – verhindert die meisten Streitfälle.
3. Prometheus-Exporter – Serverlast endlich in Grafana.
4. Neustart-Countdown, Wartungsmodus – kleine Mühe, oft gebraucht.
5. Vertrauenskasse digital – passt zum Spawn-Marktviertel.
