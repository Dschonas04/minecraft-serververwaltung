#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Wertet die Mod ChestLogger aus: wer hat aus den Kisten bestimmter Besitzer etwas genommen?
Nutzt die Besitzerliste world/chestlogger/claims.json und fragt jede Kiste per RCON ab (/chestlog inspect).

  truhenlog.py --besitzer Spieler1,Spieler2 [--seit 2026-10-10] [--alle]
"""
import argparse, collections, json, os, re
from mcwerkzeug import Rcon, server_verzeichnis, welt_verzeichnis

EINTRAG = re.compile(r'\[(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\] #(\d+) (\S+) \(([A-Z_]+)\): (.*?) @ \((-?\d+), (-?\d+), (-?\d+)\)')


def entpacken(p):
    x = p >> 38
    z = (p >> 12) & 0x3FFFFFF
    z = z - (1 << 26) if z >= 1 << 25 else z
    y = p & 0xFFF
    y = y - (1 << 12) if y >= 1 << 11 else y
    return x, y, z


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--server')
    p.add_argument('--besitzer', required=True, help='Namen mit Komma getrennt')
    p.add_argument('--seit', default='', help='nur Einträge ab diesem Datum (JJJJ-MM-TT)')
    p.add_argument('--alle', action='store_true', help='auch Einträge der Besitzer selbst zeigen')
    a = p.parse_args()
    server = server_verzeichnis(a.server)
    besitzer = set(a.besitzer.split(','))
    claims = json.load(open(os.path.join(welt_verzeichnis(server), 'chestlogger', 'claims.json')))['claims']
    gesehen, eintraege = set(), []
    with Rcon(server) as rcon:
        for c in claims:
            if c['ownerName'] not in besitzer:
                continue
            x, y, z = entpacken(c['pos'])
            seite = 1
            while True:
                antwort = re.sub('§.', '', rcon.befehl(f'chestlog inspect {x} {y} {z} {seite}'))
                for e in EINTRAG.findall(antwort):
                    if e[1] not in gesehen:
                        gesehen.add(e[1])
                        eintraege.append((c['ownerName'],) + e)
                m = re.search(r'Page (\d+)/(\d+)', antwort)
                if not m or int(m.group(1)) >= int(m.group(2)) or seite >= 50:
                    break
                seite += 1
    print('Einträge:', len(eintraege), ' neuester:', max((e[1] for e in eintraege), default='-'))
    for besitzer_, datum, _, wer, aktion, aenderung, *ort in sorted(eintraege, key=lambda e: e[1]):
        if datum < a.seit or (wer == besitzer_ and not a.alle):
            continue
        if a.alle or 'EXTRACT' in aktion or 'PICKUP' in aktion or 'BREAK' in aktion or 'DROP' in aktion or aenderung.startswith('-'):
            print(datum, wer, aktion, 'Kiste von', besitzer_, '@', ' '.join(ort), aenderung[:150])


if __name__ == '__main__':
    main()
