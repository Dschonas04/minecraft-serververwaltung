#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Runder Portalplatz mit entzündetem Nether-Portal im Norden und, wenn die Mod Aerial Hell installiert ist,
einem Aerial-Hell-Portal im Süden. Steinboden mit Kompassmitte, Laternen am Rand.

--mitte ist die Platzmitte (Bodenhöhe). Der Platz hat Radius 9; die Portale stehen 7 Blöcke nördlich und
südlich der Mitte und schauen zur Mitte.

  portalplatz.py --mitte "22 62 0" --aerialhell -o portale.txt
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt, text

A = 'aerialhell:'


def portal(m, zp, richtung, rahmen, portalblock, rand, mitte_oben, kappe, laterne, stufe, schildholz, schild, farbe):
    m.fill(-2, 1, zp, 2, 6, zp, rahmen)
    m.fill(-3, 1, zp, -3, 7, zp, rand)
    m.fill(3, 1, zp, 3, 7, zp, rand)
    m.fill(-3, 7, zp, 3, 7, zp, rand)
    m.setblock(0, 7, zp, mitte_oben)
    for x in (-3, 3):
        m.setblock(x, 8, zp, kappe)
        m.setblock(x, 9, zp, laterne)
    m.fill(-1, 1, zp - richtung, 1, 1, zp - richtung, f'{stufe}[facing={"north" if richtung < 0 else "south"}]')
    for x in (-3, 3):
        m.setblock(x, 4, zp - richtung, '%s[facing=%s]{front_text:{color:"%s",has_glowing_text:1b,messages:["","%s","",""]}}'
                   % (schildholz, 'south' if richtung < 0 else 'north', farbe, text(schild)))
    m.fill(-1, 2, zp, 1, 5, zp, portalblock)


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--mitte', type=punkt, required=True, help='Platzmitte "x y z" (Bodenhöhe)')
    p.add_argument('--aerialhell', action='store_true', help='auch ein Aerial-Hell-Portal (Mod Aerial Hell nötig)')
    args = p.parse_args()
    bau = Bau()
    m = Versatz(bau, *args.mitte)
    R = 9
    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.hypot(x, z)
            if r > R + 0.5:
                continue
            m.fill(x, 1, z, x, 12, z, 'air')
            if r > R - 1: b = 'polished_andesite'
            elif r < 1.5: b = 'chiseled_stone_bricks'
            elif r < 2.5: b = 'polished_andesite'
            elif z <= -3: b = 'polished_blackstone_bricks'
            elif z >= 3 and args.aerialhell: b = A + 'stellar_stone_bricks'
            else: b = 'stone_bricks'
            m.setblock(x, 0, z, b)
    for a in (30, 150, 210, 330):
        x = round((R - 0.5) * math.cos(math.radians(a)))
        z = round((R - 0.5) * math.sin(math.radians(a)))
        m.fill(x, 1, z, x, 2, z, 'stone_brick_wall')
        m.setblock(x, 3, z, 'lantern')

    m.fill(-4, 0, -9, 4, 0, -6, 'polished_blackstone_bricks')
    for x, z in ((-3, -6), (3, -6)):
        m.setblock(x, 0, z, 'magma_block')
    for x, z in ((-5, -8), (-6, -7), (5, -8), (6, -7), (-5, -6), (5, -6)):
        m.setblock(x, 0, z, 'crimson_nylium')
    for x, z, b in ((-5, -8, 'crimson_fungus'), (-6, -7, 'crimson_roots'), (5, -8, 'crimson_roots'), (6, -7, 'crimson_fungus')):
        m.setblock(x, 1, z, b)
    m.setblock(-4, 1, -7, 'soul_campfire')
    m.setblock(4, 1, -7, 'soul_campfire')
    m.fill(-3, 1, -8, 3, 7, -8, 'polished_blackstone')
    portal(m, -7, -1, 'obsidian', 'nether_portal[axis=x]', 'polished_blackstone_bricks', 'crying_obsidian',
           'polished_blackstone_brick_wall', 'soul_lantern', 'polished_blackstone_brick_stairs', 'crimson_wall_sign', 'Nether', 'orange')
    m.setblock(-3, 7, -7, 'gilded_blackstone')
    m.setblock(3, 7, -7, 'gilded_blackstone')

    if args.aerialhell:
        m.fill(-4, 0, 6, 4, 0, 9, A + 'stellar_stone_bricks')
        for x, z in ((-5, 8), (-6, 7), (5, 8), (6, 7), (-5, 6), (5, 6)):
            m.setblock(x, 0, z, A + 'stellar_grass_block')
        for x, z, b in ((-5, 8, 'glowing_boletus'), (-6, 7, 'stellar_tall_grass'), (5, 8, 'stellar_fern'), (6, 7, 'glowing_boletus')):
            m.setblock(x, 1, z, A + b)
        for x in (-4, 4):
            m.setblock(x, 1, 7, A + 'crystal_block')
            m.setblock(x, 2, 7, A + 'potted_vibrant_sky_cactus')
        m.fill(-3, 1, 8, 3, 7, 8, A + 'stellar_stone')
        portal(m, 7, 1, A + 'stellar_portal_frame_block', A + 'aerial_hell_portal[axis=x]', A + 'stellar_stone_bricks',
               A + 'lunatic_crystal_block', A + 'stellar_stone_bricks_wall', A + 'crystallized_lantern',
               A + 'stellar_stone_bricks_stairs', A + 'aerial_tree_wall_sign', 'Aerial Hell', 'light_blue')
        m.setblock(-3, 7, 7, A + 'crystal_block')
        m.setblock(3, 7, 7, A + 'crystal_block')
        for x, y, z in ((-2, 11, 8), (-1, 11, 8), (0, 12, 8), (1, 11, 8), (-1, 12, 8), (2, 11, 9), (-4, 12, 9), (-3, 12, 9)):
            m.setblock(x, y, z, A + 'golden_solid_ether')
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
