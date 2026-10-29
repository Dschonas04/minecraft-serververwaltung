#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Befehle per RCON an den Server schicken. Kennwort und Port aus server.properties.

  rcon.py list                      ein Befehl
  rcon.py "say Hallo" "list"        mehrere
  rcon.py -f befehle.txt            aus Datei: eine Zeile je Befehl, 'sleep N' pausiert, '#' ist Kommentar
  bau/teich.py ... | rcon.py -f -   aus der Standardeingabe
"""
import argparse, sys
from mcwerkzeug import Rcon, ausfuehren, server_verzeichnis


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('befehle', nargs='*')
    p.add_argument('-f', '--datei', help="Befehlsdatei oder '-' für die Standardeingabe")
    p.add_argument('--server', help='Server-Verzeichnis (sonst MC_DIR oder aktuelles Verzeichnis)')
    args = p.parse_args()
    server = server_verzeichnis(args.server)
    if args.datei:
        zeilen = (sys.stdin if args.datei == '-' else open(args.datei, encoding='utf-8')).read().splitlines()
        ausfuehren(server, zeilen)
    elif args.befehle:
        with Rcon(server) as rcon:
            for befehl in args.befehle:
                print(rcon.befehl(befehl))
    else:
        p.print_help()


if __name__ == '__main__':
    main()
