#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Ersetzt Blöcke in einem Gebiet, z. B. Spuren von Explosionen oder Mod-Blöcke.

  ersetzen.py --mitte "0 0" --radius 96 --von 55 --bis 110 --tausch tnt_arsenal:irradiated_earth=grass_block \\
      --tausch tnt_arsenal:fallout=air -o aufraeumen.txt
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, ausgeben, bau_parser, punkt


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--mitte', type=punkt, required=True, help='"x z"')
    p.add_argument('--radius', type=int, required=True)
    p.add_argument('--von', type=int, default=-64, help='unterste Höhe')
    p.add_argument('--bis', type=int, default=320, help='oberste Höhe')
    p.add_argument('--tausch', action='append', required=True, help='"alt=neu", mehrfach')
    args = p.parse_args()
    cx, cz = args.mitte
    bau = Bau()
    for x in range(cx - args.radius, cx + args.radius + 1, 16):
        for z in range(cz - args.radius, cz + args.radius + 1, 16):
            x2, z2 = min(x + 15, cx + args.radius), min(z + 15, cz + args.radius)
            for paar in args.tausch:
                alt, neu = paar.split('=', 1)
                bau.fill(x, args.von, z, x2, args.bis, z2, neu, alt)
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
