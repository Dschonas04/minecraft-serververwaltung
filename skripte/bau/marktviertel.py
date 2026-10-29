#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Marktviertel: gepflasterte Straße mit Ständen auf beiden Seiten (Fass-Theke, Lagerfässer,
gestreifte Markise, Laternen), Laternenpfählen, Deko und Brunnen am Ende.

--ort ist der Straßenanfang: Mitte der Straße, Bodenhöhe. Die Straße läuft von dort nach Westen (-x),
die Stände liegen nördlich und südlich. Vor dem Bauen die Regionsdateien sichern.

  marktviertel.py --ort "-10 62 0" --staende 5 -o markt.txt
  marktviertel.py --ort "-10 62 0" --senden
"""
import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt, text

FARBEN = [('red', 'white'), ('blue', 'white'), ('yellow', 'orange'), ('green', 'lime'), ('purple', 'magenta'),
          ('cyan', 'light_blue'), ('brown', 'orange'), ('red', 'yellow'), ('blue', 'light_blue'), ('lime', 'white')]


def stand(m, x1, seite, c1, c2):
    """Ein Stand, 5 breit, 6 tief; seite -1 = Nordseite, +1 = Südseite der Straße."""
    x2 = x1 + 4
    zf, zb = (-5, -10) if seite < 0 else (5, 10)
    lo, hi = min(zf, zb), max(zf, zb)
    vorne = 'south' if seite < 0 else 'north'
    m.fill(x1, 0, lo, x2, 0, hi, 'spruce_planks')
    m.fill(x1, 0, zf - seite, x2, 0, zf - seite, 'polished_andesite')
    for x in (x1, x2):
        for z in (zf, zb):
            m.fill(x, 1, z, x, 4, z, 'stripped_spruce_log')
    m.fill(x1 + 1, 1, zb, x2 - 1, 3, zb, 'spruce_planks')
    m.fill(x1 + 1, 4, zb, x2 - 1, 4, zb, 'spruce_slab[type=bottom]')
    for x in (x1, x2):
        m.fill(x, 1, lo + 1, x, 1, hi - 1, 'spruce_fence')
    m.fill(x1 + 1, 1, zf, x2 - 1, 1, zf, 'barrel[facing=up]')
    m.fill(x1 + 1, 1, zb - seite, x2 - 1, 2, zb - seite, f'barrel[facing={vorne}]')
    for x in range(x1, x2 + 1):
        farbe = c1 if (x - x1) % 2 == 0 else c2
        m.fill(x, 5, lo - (1 if seite > 0 else 0), x, 5, hi + (1 if seite < 0 else 0), f'{farbe}_wool')
    m.setblock(x1 + 1, 4, zf, 'lantern[hanging=true]')
    m.setblock(x2 - 1, 4, zf, 'lantern[hanging=true]')


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--ort', type=punkt, required=True, help='Straßenanfang "x y z" (Mitte, Bodenhöhe)')
    p.add_argument('--staende', type=int, default=5, help='Stände je Straßenseite (Vorgabe 5)')
    p.add_argument('--schild', default='Marktviertel', help='Text auf dem Eingangsschild')
    p.add_argument('--zufall', type=int, default=1012, help='Startwert für das Pflastermuster')
    args = p.parse_args()
    random.seed(args.zufall)
    bau = Bau()
    m = Versatz(bau, *args.ort)
    starts = [-8 - 7 * k for k in range(args.staende)]
    ende = starts[-1] - 1
    m.fill(ende, 0, -12, -1, 18, 12, 'air')
    m.fill(ende, -1, -12, -1, -1, 12, 'dirt')
    m.fill(ende, 0, -12, -1, 0, 12, 'grass_block')
    m.fill(ende, 0, -3, 0, 0, 3, 'polished_andesite')
    m.fill(ende, 0, -2, 0, 0, 2, 'stone_bricks')
    for x in range(ende, 1):
        for z in range(-2, 3):
            r = random.random()
            if r < 0.12: m.setblock(x, 0, z, 'mossy_stone_bricks')
            elif r < 0.22: m.setblock(x, 0, z, 'cracked_stone_bricks')
    i = 0
    for seite in (-1, 1):
        for x1 in starts:
            stand(m, x1, seite, *FARBEN[i % len(FARBEN)])
            i += 1
    for x in [-2] + [s - 2 for s in starts[:-1]]:
        for z in (-4, 4):
            m.fill(x, 1, z, x, 3, z, 'spruce_fence')
            m.setblock(x, 4, z, 'lantern')
    for k, s in enumerate(starts[:-1]):
        z = (-8, 7, -6, 8)[k % 4]
        m.setblock(s - 1, 1, z, 'hay_block')
        m.setblock(s - 1, 1, 9 if z > 0 else -9, 'barrel[facing=up]')
    # Brunnen am Ende
    m.fill(ende, 0, -1, ende + 2, 0, 1, 'stone_bricks')
    m.fill(ende, 1, -1, ende + 2, 1, 1, 'stone_brick_wall')
    m.setblock(ende + 1, 1, 0, 'water')
    # Eingangsschild
    m.fill(-1, 1, -3, -1, 3, -3, 'spruce_fence')
    m.setblock(-1, 4, -3, 'lantern')
    m.setblock(0, 2, -3, 'spruce_wall_sign[facing=east]{front_text:{messages:["","%s","",""]}}' % text(args.schild))
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
