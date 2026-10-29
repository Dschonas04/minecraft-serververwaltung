#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Gerader Trampelpfad mit Laternenpfählen im Wechsel links und rechts. Läuft entlang x oder z
(von --von nach --bis; bei schrägen Strecken erst x, dann z).

  weg.py --von "0 -10" --bis "0 -29" --hoehe 62 --breite 3 --laternen 7 -o weg.txt
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, ausgeben, bau_parser, punkt


def strecke(bau, a, b, festes, entlang_x, y, halb, block, abstand, start):
    lo, hi = min(a, b), max(a, b)
    if entlang_x:
        bau.fill(lo, y, festes - halb, hi, y, festes + halb, block)
        bau.fill(lo, y + 1, festes - halb, hi, y + 3, festes + halb, 'air')
    else:
        bau.fill(festes - halb, y, lo, festes + halb, y, hi, block)
        bau.fill(festes - halb, y + 1, lo, festes + halb, y + 3, hi, 'air')
    if not abstand:
        return start
    schritt = 1 if b >= a else -1
    for i, pos in enumerate(range(a + schritt * 3, b, schritt * abstand)):
        seite = (halb + 2) * (1 if (start + i) % 2 else -1)
        x, z = (pos, festes + seite) if entlang_x else (festes + seite, pos)
        bau.setblock(x, y, z, 'cobblestone')
        bau.fill(x, y + 1, z, x, y + 2, z, 'spruce_fence')
        bau.setblock(x, y + 3, z, 'lantern')
    return start + len(range(a + schritt * 3, b, schritt * abstand))


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--von', type=punkt, required=True, help='"x z"')
    p.add_argument('--bis', type=punkt, required=True, help='"x z"')
    p.add_argument('--hoehe', type=int, required=True, help='Bodenhöhe des Wegs')
    p.add_argument('--breite', type=int, default=3)
    p.add_argument('--block', default='dirt_path')
    p.add_argument('--laternen', type=int, default=7, help='Abstand der Laternen, 0 = keine')
    args = p.parse_args()
    bau = Bau()
    (x1, z1), (x2, z2) = args.von, args.bis
    halb = args.breite // 2
    n = 0
    if x1 != x2:
        n = strecke(bau, x1, x2, z1, True, args.hoehe, halb, args.block, args.laternen, n)
    if z1 != z2:
        strecke(bau, z1, z2, x2, False, args.hoehe, halb, args.block, args.laternen, n)
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
