#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Fichtenhütte 9x9 mit Satteldach: Bett, Fässer, Werkbank, Ofen, Räucherofen, Hängelaterne, Namensschild.

--ort ist die Nordwestecke des Fundaments (Bodenhöhe); die Tür liegt mittig auf der Nordseite.

  huette.py --ort "14 62 16" --besitzer "Jonas" -o huette.txt
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt, text


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--ort', type=punkt, required=True, help='Nordwestecke "x y z" (Bodenhöhe)')
    p.add_argument('--besitzer', default='', help='Name auf dem Schild über der Tür')
    p.add_argument('--bett', default='red', help='Farbe von Bett und Teppich')
    args = p.parse_args()
    bau = Bau()
    m = Versatz(bau, *args.ort)
    m.fill(-2, 0, -2, 10, 16, 10, 'air')
    m.fill(-2, -1, -2, 10, -1, 10, 'dirt')
    m.fill(-1, 0, -1, 9, 0, 9, 'grass_block')
    m.fill(0, 0, 0, 8, 0, 8, 'cobblestone')
    m.fill(1, 0, 1, 7, 0, 7, 'spruce_planks')
    m.fill(0, 1, 0, 8, 4, 8, 'spruce_planks')
    m.fill(1, 1, 1, 7, 4, 7, 'air')
    for x in (0, 8):
        for z in (0, 8):
            m.fill(x, 1, z, x, 4, z, 'spruce_log')
    for x1, z1, x2, z2 in [(0, 3, 0, 5), (8, 3, 8, 5), (2, 8, 3, 8), (5, 8, 6, 8), (6, 0, 6, 0), (2, 0, 2, 0)]:
        m.fill(x1, 2, z1, x2, 3, z2, 'glass_pane')
    m.setblock(4, 1, 0, 'spruce_door[facing=south,half=lower,hinge=left]')
    m.setblock(4, 2, 0, 'spruce_door[facing=south,half=upper,hinge=left]')
    for k in range(5):
        m.fill(-1, 5 + k, -1 + k, 9, 5 + k, -1 + k, 'spruce_stairs[facing=south]')
        m.fill(-1, 5 + k, 9 - k, 9, 5 + k, 9 - k, 'spruce_stairs[facing=north]')
    m.fill(-1, 9, 4, 9, 9, 4, 'spruce_planks')
    for k in range(4):
        for x in (0, 8):
            m.fill(x, 5 + k, k, x, 5 + k, 8 - k, 'spruce_planks')
    m.fill(0, 5, 0, 8, 5, 0, 'spruce_planks')
    m.fill(0, 5, 8, 8, 5, 8, 'spruce_planks')
    m.setblock(6, 1, 6, f'{args.bett}_bed[part=foot,facing=south]')
    m.setblock(6, 1, 7, f'{args.bett}_bed[part=head,facing=south]')
    m.fill(1, 1, 3, 1, 2, 7, 'barrel[facing=east]')
    m.fill(2, 1, 7, 3, 2, 7, 'barrel[facing=north]')
    m.setblock(1, 1, 1, 'barrel[facing=up]')
    m.setblock(1, 1, 2, 'barrel[facing=up]')
    m.setblock(7, 1, 1, 'crafting_table')
    m.setblock(7, 1, 2, 'furnace[facing=west]')
    m.setblock(7, 1, 3, 'smoker[facing=west]')
    m.fill(3, 1, 3, 5, 1, 5, f'{args.bett}_carpet')
    m.setblock(7, 1, 7, 'flower_pot')
    m.setblock(4, 8, 4, 'iron_chain[axis=y]')
    m.setblock(4, 7, 4, 'lantern[hanging=true]')
    if args.besitzer:
        titel = f"{args.besitzer}' Hütte" if args.besitzer.endswith(('s', 'x', 'z', 'ß')) else f'{args.besitzer}s Hütte'
        m.setblock(4, 3, -1, 'spruce_wall_sign[facing=north]{front_text:{messages:["","%s","",""]}}' % text(titel))
    for x in (2, 6):
        m.setblock(x, 1, -1, 'spruce_fence')
        m.setblock(x, 2, -1, 'lantern')
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
