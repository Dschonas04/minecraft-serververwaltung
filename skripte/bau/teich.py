#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Natürlicher Teich: leicht unregelmäßiger Rand, bis zu 3 Blöcke tief, Sand/Kies/Ton am Grund,
Seegras, Seerosen und Zuckerrohr am Ufer.

--mitte ist die Mitte der Wasseroberfläche (Höhe = Bodenhöhe des Geländes).

  teich.py --mitte "0 62 -41" --rx 16 --rz 11 -o teich.txt
"""
import math, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--mitte', type=punkt, required=True)
    p.add_argument('--rx', type=int, default=12, help='Halbachse in x-Richtung')
    p.add_argument('--rz', type=int, default=8, help='Halbachse in z-Richtung')
    p.add_argument('--tiefe', type=int, default=3, help='größte Tiefe')
    p.add_argument('--zufall', type=int, default=4711)
    args = p.parse_args()
    random.seed(args.zufall)
    bau = Bau()
    m = Versatz(bau, *args.mitte)
    for x in range(-args.rx - 2, args.rx + 3):
        for z in range(-args.rz - 2, args.rz + 3):
            winkel = math.atan2(z, x)
            d = math.hypot(x / args.rx, z / args.rz) / (1 + 0.08 * math.sin(3 * winkel) + 0.05 * math.cos(5 * winkel))
            if d <= 1:
                tiefe = max(1, round(args.tiefe * (1 - d) / 0.55)) if d > 0.45 else args.tiefe
                tiefe = min(args.tiefe, tiefe)
                m.fill(x, -tiefe + 1, z, x, 0, z, 'water')
                m.fill(x, 1, z, x, 3, z, 'air')
                m.setblock(x, -tiefe, z, random.choice(['sand', 'sand', 'gravel', 'clay']) if tiefe > 1 else 'sand')
                if tiefe >= 2 and random.random() < 0.25:
                    m.setblock(x, -tiefe + 1, z, 'seagrass')
                if d < 0.9 and tiefe <= 2 and random.random() < 0.06:
                    m.setblock(x, 1, z, 'lily_pad')
            elif d <= 1.12:
                m.setblock(x, 0, z, random.choice(['sand', 'sand', 'gravel', 'grass_block', 'grass_block', 'coarse_dirt']))
                if random.random() < 0.10:
                    m.setblock(x, 1, z, 'sugar_cane')
                    if random.random() < 0.6:
                        m.setblock(x, 2, z, 'sugar_cane')
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
