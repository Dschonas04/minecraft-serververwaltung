#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Liest die Welt direkt aus den Regionsdateien (nur lesend, auch bei laufendem Server).

  scan.py hoehen  --mitte "0 0" --radius 64 [--raster 4]     Höhenkarte, ~ = Wasser
  scan.py gebaut  --mitte "0 0" --radius 64                  Blöcke, die nach Bauwerk aussehen, mit Fläche
  scan.py wasser  --mitte "0 0" --radius 96 [--max 40]       kleine, abgeschlossene Wasserstellen
                  [--fuellen -o fuellen.txt | --senden]      ... und durch Gras ersetzen

Vor dem Speichern der Welt (save-all flush) sind die neuesten Änderungen noch nicht in den Dateien.
"""
import argparse, collections, os, sys
from mcwerkzeug import Bau, LUFT, Welt, ausgeben, name, punkt, region_verzeichnis, server_verzeichnis

WEICH = ('leaves', 'log', 'grass', 'flower', 'daisy', 'bluet', 'poppy', 'tulip', 'fern', 'bush', 'petals', 'snow',
         'vine', 'sapling', 'short', 'tall', 'dandelion', 'azalea', 'moss_carpet', 'lilac', 'rose', 'peony', 'mushroom',
         'sugar', 'kelp', 'seagrass', 'lily', 'pumpkin', 'melon', 'cactus', 'berry', 'dripleaf', 'leaf_litter', 'cocoa')
GEBAUT = ('planks', 'brick', 'slab', 'stairs', 'fence', 'door', 'glass', 'polished', 'chest', 'barrel', 'torch',
          'lantern', 'bed', 'crafting', 'furnace', 'wool', 'concrete', 'carpet', 'sign', 'wall', 'trapdoor', 'smooth',
          'cut_', 'lamp', 'rail', 'tile', 'hay', 'bookshelf', 'anvil', 'glazed', 'scaffold', 'ladder')


def oberflaeche(welt, x, z):
    for y in range(319, -64, -1):
        b = welt.block(x, y, z)
        if b is None:
            return None
        n = name(b)
        if n in LUFT or any(k in n.split(':')[1] for k in WEICH if not n.endswith('grass_block')):
            continue
        return y, n.split(':')[1]


def hoehen(welt, a):
    cx, cz = a.mitte
    for z in range(cz - a.radius, cz + a.radius + 1, a.raster):
        zeile = ''
        for x in range(cx - a.radius, cx + a.radius + 1, a.raster):
            o = oberflaeche(welt, x, z)
            zeile += '  ??' if o is None else ('~' if o[1] in ('water', 'ice') else ' ') + f'{o[0]:3d}'
        print(f'{z:5d}', zeile)


def gebaut(welt, a):
    cx, cz = a.mitte
    funde = collections.defaultdict(list)
    for x in range(cx - a.radius, cx + a.radius + 1):
        for z in range(cz - a.radius, cz + a.radius + 1):
            o = oberflaeche(welt, x, z)
            if o is None:
                continue
            for y in range(o[0] + 24, o[0] - 6, -1):
                n = name(welt.block(x, y, z))
                if not n or n in LUFT:
                    continue
                kurz = n.split(':')[1]
                if not n.startswith('minecraft:') or any(k in kurz for k in GEBAUT):
                    funde[n].append((x, y, z))
    for n, orte in sorted(funde.items(), key=lambda e: -len(e[1])):
        xs, ys, zs = zip(*orte)
        print(f'{len(orte):6d}  {n:45s} x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}  z {min(zs)}..{max(zs)}')


def wasser(welt, a):
    cx, cz = a.mitte
    w = set()
    for x in range(cx - a.radius, cx + a.radius + 1):
        for z in range(cz - a.radius, cz + a.radius + 1):
            for y in range(a.unten, a.oben + 1):
                if name(welt.block(x, y, z)) == 'minecraft:water':
                    w.add((x, y, z))
    gesehen, klein = set(), []
    for start in w:
        if start in gesehen:
            continue
        gruppe, stapel = [], [start]
        gesehen.add(start)
        while stapel:
            q = stapel.pop()
            gruppe.append(q)
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                n = (q[0] + d[0], q[1] + d[1], q[2] + d[2])
                if n in w and n not in gesehen:
                    gesehen.add(n)
                    stapel.append(n)
        if len(gruppe) <= a.max and not any(abs(x - cx) == a.radius or abs(z - cz) == a.radius for x, _, z in gruppe):
            klein.append(gruppe)
    for g in sorted(klein, key=len):
        print(f'{len(g):4d} Blöcke bei {min(g)}', file=sys.stderr)
    if a.fuellen:
        bau = Bau()
        for g in klein:
            for x, y, z in sorted(g, key=lambda p: -p[1]):
                bau.setblock(x, y, z, 'dirt' if (x, y + 1, z) in g else 'grass_block')
        ausgeben(bau, a)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('art', choices=('hoehen', 'gebaut', 'wasser'))
    p.add_argument('--server')
    p.add_argument('--dimension', default='minecraft:overworld')
    p.add_argument('--mitte', type=punkt, default=(0, 0), help='"x z"')
    p.add_argument('--radius', type=int, default=48)
    p.add_argument('--raster', type=int, default=4, help='Rasterweite der Höhenkarte')
    p.add_argument('--max', type=int, default=40, help='größte Wasserstelle, die noch als klein gilt')
    p.add_argument('--unten', type=int, default=55, help='Wassersuche ab dieser Höhe')
    p.add_argument('--oben', type=int, default=75, help='Wassersuche bis zu dieser Höhe')
    p.add_argument('--fuellen', action='store_true', help='kleine Wasserstellen zuschütten')
    p.add_argument('--senden', action='store_true')
    p.add_argument('-o', '--ausgabe')
    a = p.parse_args()
    welt = Welt(region_verzeichnis(server_verzeichnis(a.server), a.dimension))
    {'hoehen': hoehen, 'gebaut': gebaut, 'wasser': wasser}[a.art](welt, a)


if __name__ == '__main__':
    main()
