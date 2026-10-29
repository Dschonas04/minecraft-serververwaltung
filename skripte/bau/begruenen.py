#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Pflanzt Bäume und Blumenflecken auf Gras (per /place feature, also wie natürlich gewachsen).
Gebäude und Wege sind über --frei ausgespart.

  begruenen.py --mitte "0 62 0" --radius 60 --baeume 25 --blumen 40 --frei "-48 -19 -10 12" --frei "-12 -12 12 12"
"""
import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, ausgeben, bau_parser, punkt

BAEUME = ['fancy_oak', 'oak', 'birch', 'fancy_oak', 'oak_bees_005', 'birch_bees_005']
BLUMEN = ['flower_default', 'flower_plain', 'flower_meadow', 'flower_flower_forest']


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--mitte', type=punkt, required=True, help='"x y z", y = Bodenhöhe')
    p.add_argument('--radius', type=int, default=48)
    p.add_argument('--baeume', type=int, default=20)
    p.add_argument('--blumen', type=int, default=30)
    p.add_argument('--abstand', type=int, default=6, help='Mindestabstand zwischen Bäumen')
    p.add_argument('--frei', type=punkt, action='append', default=[], help='Sperrfläche "x1 z1 x2 z2", mehrfach')
    p.add_argument('--zufall', type=int, default=4711)
    args = p.parse_args()
    random.seed(args.zufall)
    cx, y, cz = args.mitte
    bau = Bau()

    def frei(x, z):
        return all(not (min(a, c) <= x <= max(a, c) and min(b, d) <= z <= max(b, d)) for a, b, c, d in args.frei)

    gesetzt = []
    versuche = 0
    while len(gesetzt) < args.baeume and versuche < args.baeume * 50:
        versuche += 1
        x, z = cx + random.randint(-args.radius, args.radius), cz + random.randint(-args.radius, args.radius)
        if frei(x, z) and all((x - a) ** 2 + (z - b) ** 2 >= args.abstand ** 2 for a, b in gesetzt):
            gesetzt.append((x, z))
            bau.befehl(f'place feature minecraft:{random.choice(BAEUME)} {x} {y + 1} {z}', (x, z))
    for _ in range(args.blumen):
        x, z = cx + random.randint(-args.radius, args.radius), cz + random.randint(-args.radius, args.radius)
        if frei(x, z):
            bau.befehl(f'place feature minecraft:{random.choice(BLUMEN)} {x} {y + 1} {z}', (x, z))
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
