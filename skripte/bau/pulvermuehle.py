#!/usr/bin/env python3
"""Schwarzpulver-Mühle mit Create (Mod create_ultimate_factory): offene Hütte mit Wasserrad, Mixer und Becken.
Kohle oder Holzkohle und Lohenstaub in die obere Kiste, unten kommt Schwarzpulver heraus
(2 Kohle + 1 Lohenstaub = 3 Schwarzpulver).

Antrieb: kleines Wasserrad (8 U/min, 256 SU) über Getriebe und zwei Zahnradstufen auf 32 U/min – der Mixer braucht
mindestens 30. Das Becken gibt auf ein Depot aus, ein Trichter darunter füllt die Ausgabekiste.

--mitte ist der Boden unter dem Becken (oberster fester Block); die Vorderseite mit den Kisten zeigt nach Norden.

  pulvermuehle.py --mitte "-96 62 10" -o muehle.txt
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt, text

C = 'create:'


def schild(m, x, y, z, *zeilen):
    """Stehendes Schild, Schrift nach Norden."""
    zeilen = list(zeilen) + [''] * (4 - len(zeilen))
    m.setblock(x, y, z, 'spruce_sign[rotation=8]{front_text:{messages:[%s]}}' % ','.join('"%s"' % text(z_) for z_ in zeilen))


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--mitte', type=punkt, required=True, help='Boden unter dem Becken "x y z"')
    args = p.parse_args()
    bau = Bau()
    m = Versatz(bau, *args.mitte)

    # Hütte: Boden, Eckpfosten, Dach, Licht
    m.fill(-3, 1, -3, 5, 8, 5, 'air')
    m.fill(-3, 0, -3, 5, 0, 5, 'polished_andesite')
    for x, z in ((-3, -3), (5, -3), (-3, 5), (5, 5)):
        m.fill(x, 1, z, x, 7, z, 'stripped_spruce_log')
    m.fill(-3, 8, -3, 5, 8, 5, 'spruce_slab[type=bottom]')
    m.fill(-3, 7, -3, 5, 7, -3, 'spruce_planks')
    m.fill(-3, 7, 5, 5, 7, 5, 'spruce_planks')
    m.fill(-3, 7, -3, -3, 7, 5, 'spruce_planks')
    m.fill(5, 7, -3, 5, 7, 5, 'spruce_planks')
    for x, z in ((-2, -2), (4, -2), (-2, 4), (4, 4), (1, -2), (-2, 1)):
        m.setblock(x, 6, z, 'lantern[hanging=true]')

    # Ausgabe: Depot -> Trichter -> Kiste (vorn auf dem Boden)
    m.setblock(0, 1, -2, 'chest[facing=north]')
    m.setblock(0, 1, -1, 'hopper[facing=north]')
    m.setblock(0, 2, -1, C + 'depot')
    # Becken (gibt nach Norden aufs Depot aus), darunter ein Stützblock, darüber der Mixer
    m.setblock(0, 2, 0, 'polished_andesite')
    m.setblock(0, 3, 0, C + 'basin[facing=north]')
    m.setblock(0, 5, 0, C + 'mechanical_mixer')
    # Eingabe: Kiste -> Trichter -> Becken
    m.setblock(-1, 3, 0, 'hopper[facing=east]')
    m.setblock(-1, 4, 0, 'chest[facing=west]')
    m.fill(-2, 1, 0, -2, 2, 0, 'spruce_planks')        # Tritt zur Eingabekiste
    m.setblock(-2, 1, -1, 'spruce_stairs[facing=south]')

    # Antrieb: Wasserrad -> Welle -> Getriebe -> Welle hoch -> groß/klein -> groß -> Mixer (8 -> 16 -> 32 U/min)
    m.setblock(4, 1, 2, C + 'water_wheel[facing=east]')
    m.setblock(3, 1, 2, C + 'shaft[axis=x]')
    m.setblock(2, 1, 2, C + 'gearbox[axis=z]')
    m.fill(2, 2, 2, 2, 3, 2, C + 'shaft[axis=y]')
    m.setblock(2, 4, 2, C + 'large_cogwheel[axis=y]')
    m.setblock(1, 4, 1, C + 'cogwheel[axis=y]')
    m.setblock(1, 5, 1, C + 'large_cogwheel[axis=y]')
    # Wasser fällt an der Südseite des Rades herunter, eingefasst
    m.fill(3, 1, 3, 3, 3, 3, 'stone_bricks')
    m.fill(5, 1, 3, 5, 3, 3, 'stone_bricks')
    m.fill(4, 1, 4, 4, 3, 4, 'stone_bricks')
    m.setblock(4, 3, 2, 'stone_bricks')
    m.setblock(4, 4, 3, 'stone_bricks')
    m.setblock(4, 3, 3, 'water')

    schild(m, 1, 1, -2, 'Ausgabe:', 'Schwarzpulver')
    schild(m, -1, 5, 0, 'Eingabe:', 'Kohle/Holzkohle', '+ Lohenstaub')
    schild(m, 3, 1, -3, 'Schwarzpulver-Mühle', '2 Kohle + 1 Lohen-', 'staub = 3 Pulver')
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
