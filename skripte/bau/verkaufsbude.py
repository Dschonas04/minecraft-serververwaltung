#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Große Verkaufsbude mit Händler: Fass-Theke, Lagerfässer, Leuchtrahmen mit der Ware an der Rückwand,
Leuchtschilder und ein Schmuckstück dahinter. Zwei Stile:

  zelt    rot-weißes Zeltdach, Schachbrettboden, zwei weiße Deko-Raketen
  nether  Schwarzstein und Netherziegel, Seelenlaternen, große Nether-Rakete auf einer Startrampe

--ort ist die linke vordere Ecke (Westen, Thekenreihe, Bodenhöhe). Die Bude ist 12 breit (nach Osten)
und 8 tief (nach Norden), der Händler schaut nach Süden. Dahinter braucht sie 7 Blöcke Platz.
Ein erneuter Lauf mit demselben --name ersetzt Händler und Rahmen.

  verkaufsbude.py --ort "-25 62 -5" --stil nether --ware minecraft:firework_rocket --menge 64 \\
      --preis "minecraft:diamond 2" --schild "64 Raketen|Flugdauer 1|für|2 Diamanten" --titel RAKETEN
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from mcwerkzeug import Bau, Versatz, ausgeben, bau_parser, punkt, text

BREITE = 11  # x 0..11


def zelt(m):
    m.fill(-1, 0, -11, 12, 0, -8, 'grass_block')
    m.fill(1, 0, -6, 10, 0, -1, 'red_concrete')
    for x in range(2, 10):
        for z in range(-5, -1):
            m.setblock(x, 0, z, 'white_concrete' if (x + z) % 2 else 'dark_oak_planks')
    pfosten, wand, zaun = 'stripped_dark_oak_log', 'dark_oak_planks', 'dark_oak_fence'
    rahmen(m, pfosten, wand, zaun)
    m.fill(1, 3, -7, 10, 3, -7, 'red_concrete')
    for k, (z1, z2) in enumerate([(-8, 1), (-7, 0), (-6, -1), (-5, -2), (-4, -3)]):
        for x in range(-1, 13):
            m.fill(x, 6 + k, z1, x, 6 + k, z2, ('red' if x % 2 else 'white') + '_wool')
    for x in (2, 6, 9):
        m.setblock(x, 5, -2, 'lantern[hanging=true]')
        m.setblock(x, 5, -5, 'lantern[hanging=true]')
    for x in (0, 11):
        m.setblock(x, 4, 1, 'red_wall_banner[facing=south]{patterns:[{color:"white",pattern:"minecraft:rhombus"},'
                            '{color:"yellow",pattern:"minecraft:circle"}]}')
    for x in (1, 10):  # zwei Deko-Raketen hinter der Bude
        z = -9
        m.fill(x, 1, z, x, 12, z, 'white_concrete')
        for y in (4, 9, 13):
            m.setblock(x, y, z, 'red_concrete')
        m.setblock(x, 14, z, 'lightning_rod')
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m.setblock(x + dx, 1, z + dz, 'red_concrete')
            m.setblock(x + dx, 2, z + dz, 'red_terracotta')
        m.setblock(x, 0, z, 'shroomlight')
    return 'dark_oak_wall_sign', 'red', 'red'


def nether(m):
    m.fill(-1, 0, -14, 12, 0, -8, 'blackstone')
    m.fill(1, 0, -13, 11, 0, -8, 'polished_blackstone')
    m.fill(2, 0, -12, 10, 0, -8, 'polished_blackstone_bricks')
    for x, z in ((3, -12), (9, -12), (3, -8), (9, -8), (6, -13)):
        m.setblock(x, 0, z, 'magma_block')
    m.fill(0, 0, -7, 11, 0, 0, 'gilded_blackstone')
    m.fill(1, 0, -6, 10, 0, -1, 'polished_blackstone_bricks')
    for x in (2, 6, 9):
        m.setblock(x, 0, -3, 'shroomlight')
    rahmen(m, 'polished_basalt[axis=y]', 'nether_bricks', 'nether_brick_fence')
    m.fill(1, 3, -7, 10, 3, -7, 'red_nether_bricks')
    m.fill(1, 5, -7, 10, 5, -7, 'gilded_blackstone')
    m.fill(-1, 6, -8, 12, 6, 1, 'polished_blackstone_bricks')
    m.fill(-1, 6, 1, 12, 6, 1, 'gilded_blackstone')
    m.fill(-1, 7, -8, 12, 7, 1, 'nether_brick_fence')
    m.fill(0, 7, -7, 11, 7, 0, 'air')
    for x in (-1, 12, 5, 6):
        m.setblock(x, 8, 1, 'soul_lantern')
    for x in (2, 6, 9):
        m.setblock(x, 5, -2, 'soul_lantern[hanging=true]')
        m.setblock(x, 5, -5, 'soul_lantern[hanging=true]')
    for x in (0, 11):
        m.setblock(x, 4, 1, 'black_wall_banner[facing=south]{patterns:[{color:"orange",pattern:"minecraft:triangle_bottom"},'
                            '{color:"red",pattern:"minecraft:flower"},{color:"yellow",pattern:"minecraft:triangles_bottom"}]}')
    # große Nether-Rakete: Rumpf 3x3 bei x 5..7, z -11..-9
    x1, x2, z1, z2, cx, cz, top = 5, 7, -11, -9, 6, -10, 17
    m.fill(x1, 2, z1, x2, top, z2, 'red_nether_bricks')
    for y in (2, 16):
        m.fill(x1, y, z1, x2, y, z2, 'gilded_blackstone')
    m.fill(x1, 9, z1, x2, 9, z2, 'polished_blackstone_bricks')
    for x, z in ((cx, z2), (cx, z1), (x1, cz), (x2, cz)):
        m.setblock(x, 12, z, 'crying_obsidian')
        m.setblock(x, 13, z, 'crying_obsidian')
    for x, z in ((cx, cz), (x1, cz), (x2, cz), (cx, z1), (cx, z2)):
        m.setblock(x, top + 1, z, 'red_nether_bricks')
    m.setblock(cx, top + 2, cz, 'gilded_blackstone')
    m.setblock(cx, top + 3, cz, 'nether_brick_wall')
    m.setblock(cx, top + 4, cz, 'lightning_rod')
    m.fill(x1, 1, z1, x2, 1, z2, 'polished_blackstone')
    m.setblock(cx, 1, cz, 'magma_block')
    for dx, dz in ((1, 0), (-1, 0), (0, -1)):  # Flossen, nicht in die Rückwand
        for d in (2, 3):
            x, z = cx + dx * d, cz + dz * d
            m.fill(x, 1, z, x, 4 if d == 2 else 2, z, 'crimson_hyphae')
        m.setblock(cx + dx * 2, 5, cz + dz * 2, 'polished_blackstone_brick_wall')
    m.fill(1, 1, -10, 1, 18, -10, 'polished_basalt[axis=y]')  # Startturm
    for y in (8, 14):
        m.fill(2, y, -10, 4, y, -10, 'nether_brick_fence')
    m.setblock(1, 19, -10, 'soul_lantern')
    m.fill(1, 1, -11, 1, 18, -11, 'iron_chain[axis=y]')
    for x in (2, 10):
        m.setblock(x, 1, -12, 'soul_campfire')
    return 'crimson_wall_sign', 'orange', 'yellow'


def rahmen(m, pfosten, wand, zaun):
    for x in (0, 11, 4, 7):
        for z in (0, -7):
            if x in (4, 7) and z == -7:
                continue
            m.fill(x, 1, z, x, 5, z, pfosten)
    m.fill(1, 1, -7, 10, 5, -7, wand)
    for x in (0, 11):
        m.fill(x, 1, -6, x, 1, -1, zaun)
    m.fill(1, 1, 0, 10, 1, 0, 'barrel[facing=up]')  # Theke
    m.fill(1, 1, -6, 1, 3, -2, 'barrel[facing=east]')
    m.fill(10, 1, -6, 10, 3, -2, 'barrel[facing=west]')
    m.fill(3, 1, -6, 8, 1, -6, 'barrel[facing=south]')


def main():
    p = bau_parser(__doc__.split('\n\n')[0])
    p.add_argument('--ort', type=punkt, required=True, help='linke vordere Ecke "x y z" (Bodenhöhe)')
    p.add_argument('--stil', choices=('zelt', 'nether'), default='zelt')
    p.add_argument('--name', default='verkaufsbude', help='Kennung für Händler und Rahmen (Tag)')
    p.add_argument('--haendler', default='Händler', help='angezeigter Name des Händlers')
    p.add_argument('--beruf', default='fletcher', help='Beruf des Händlers (nur Aussehen)')
    p.add_argument('--ware', default='minecraft:firework_rocket', help='verkaufter Gegenstand')
    p.add_argument('--komponenten', default='', help='SNBT-Komponenten der Ware, z. B. {"minecraft:fireworks":{flight_duration:2b}}')
    p.add_argument('--menge', type=int, default=64)
    p.add_argument('--preis', default='minecraft:diamond 2', help='"Gegenstand Anzahl"')
    p.add_argument('--titel', default='', help='großes Wort auf den äußeren Schildern')
    p.add_argument('--schild', default='', help='Preisschild, Zeilen mit | getrennt (höchstens 4)')
    args = p.parse_args()

    bau = Bau()
    m = Versatz(bau, *args.ort)
    bau.befehl(f'kill @e[type=villager,tag={args.name}]', (args.ort[0], args.ort[2]))
    bau.befehl(f'kill @e[type=glow_item_frame,tag={args.name}]')
    m.fill(-1, 1, -14, 12, 26, 1, 'air')
    m.fill(-1, -1, -14, 12, -1, -8, 'dirt')
    m.fill(0, 0, 1, 11, 0, 1, 'polished_andesite')
    schildholz, farbe_titel, farbe_preis = (nether if args.stil == 'nether' else zelt)(m)

    def schild(x, zeilen, farbe):
        zeilen = (zeilen + ['', '', '', ''])[:4]
        m.setblock(x, 6, 2, '%s[facing=south]{front_text:{color:"%s",has_glowing_text:1b,messages:[%s]}}'
                   % (schildholz, farbe, ','.join('"%s"' % text(z) for z in zeilen)))
    if args.titel:
        schild(3, ['', args.titel], farbe_titel)
        schild(8, ['', args.titel], farbe_titel)
    if args.schild:
        for x in (5, 6):
            schild(x, args.schild.split('|'), farbe_preis)

    ware = '{id:"%s",count:%d%s}' % (args.ware, args.menge, f',components:{args.komponenten}' if args.komponenten else '')
    preis_item, preis_anzahl = args.preis.split()
    for x in range(2, 10):
        ax, ay, az = m.absolut(x, 4, -6)
        bau.befehl('summon glow_item_frame %d %d %d {Tags:["%s"],Facing:3b,Fixed:1b,Invulnerable:1b,Item:{id:"%s",count:1}}'
                   % (ax, ay, az, args.name, args.ware))
    hx, hy, hz = m.absolut(6, 1, -3)
    bau.befehl('summon villager %.1f %d %.1f {Tags:["%s"],NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Silent:1b,'
               'CustomName:"%s",CustomNameVisible:1b,Rotation:[0f,0f],'
               'VillagerData:{profession:"minecraft:%s",level:5,type:"minecraft:plains"},'
               'Offers:{Recipes:[{buy:{id:"%s",count:%d},sell:%s,maxUses:2147483647,rewardExp:0b,xp:0,'
               'priceMultiplier:0f,demand:0,specialPrice:0}]}}'
               % (hx - 0.5, hy, hz + 0.5, args.name, text(args.haendler), args.beruf, preis_item, int(preis_anzahl), ware))
    ausgeben(bau, args)


if __name__ == '__main__':
    main()
