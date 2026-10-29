#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Chunky nebenbei, aber nur so viel, wie der Server verkraftet.

Misst die Tickzeit (/tick query). Läuft der Server locker, rechnet Chunky weiter; wird es eng, pausiert er,
bis wieder Luft ist. Gedacht für einen systemd-Timer (siehe chunky-leerlauf.service/.timer), alle 30 s.

  chunky-leerlauf.py --weiter 25 40 --pause 32 48
"""
import argparse, re
from mcwerkzeug import Rcon, server_verzeichnis


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('--server')
    p.add_argument('--weiter', nargs=2, type=float, default=(25.0, 40.0), metavar=('MITTEL', 'P95'),
                   help='darunter (ms) darf Chunky rechnen')
    p.add_argument('--pause', nargs=2, type=float, default=(32.0, 48.0), metavar=('MITTEL', 'P95'),
                   help='darüber (ms) pausiert Chunky')
    args = p.parse_args()
    try:
        with Rcon(server_verzeichnis(args.server), timeout=20) as rcon:
            text = rcon.befehl('tick query')
            mittel = float(re.search(r'Average time per tick: ([\d.]+)ms', text).group(1))
            p95 = float(re.search(r'P95: ([\d.]+)ms', text).group(1))
            if mittel > args.pause[0] or p95 > args.pause[1]:
                befehl = 'chunky pause'
            elif mittel < args.weiter[0] and p95 < args.weiter[1]:
                befehl = 'chunky continue'
            else:
                befehl = None  # dazwischen: so lassen
            if befehl:
                rcon.befehl(befehl)
            print(f'Tick {mittel} ms, P95 {p95} ms -> {befehl or "unverändert"}')
    except (OSError, AttributeError, ValueError):
        pass  # Server startet gerade oder ist aus: beim nächsten Lauf wieder


if __name__ == '__main__':
    main()
