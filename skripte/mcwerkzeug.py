# Autor: Dschonas04 (https://github.com/Dschonas04)
"""Gemeinsame Bausteine für die Skripte: Server finden, RCON, Weltdateien lesen, Bauten ausgeben.

Das Server-Verzeichnis kommt aus --server, sonst aus der Umgebungsvariable MC_DIR, sonst ist es das
aktuelle Verzeichnis. Kennwort und Port für RCON stehen in server.properties und werden nie auf der
Befehlszeile übergeben.
"""
import argparse
import io
import os
import socket
import struct
import sys
import time
import zlib

# ---------------------------------------------------------------- Server

def server_verzeichnis(wert=None):
    pfad = wert or os.environ.get('MC_DIR') or os.getcwd()
    if not os.path.isfile(os.path.join(pfad, 'server.properties')):
        sys.exit(f'Keine server.properties in {pfad} (--server oder MC_DIR setzen)')
    return pfad


def eigenschaften(server):
    werte = {}
    with open(os.path.join(server, 'server.properties'), encoding='utf-8') as f:
        for zeile in f:
            if '=' in zeile and not zeile.lstrip().startswith('#'):
                k, v = zeile.split('=', 1)
                werte[k.strip()] = v.strip()
    return werte


def welt_verzeichnis(server):
    return os.path.join(server, eigenschaften(server).get('level-name', 'world'))


class Rcon:
    """RCON-Verbindung zum lokalen Server; Kennwort und Port aus server.properties."""

    def __init__(self, server, host='127.0.0.1', timeout=120):
        werte = eigenschaften(server)
        if werte.get('enable-rcon') != 'true' or not werte.get('rcon.password'):
            sys.exit('RCON ist nicht eingeschaltet (enable-rcon / rcon.password in server.properties)')
        self.s = socket.create_connection((host, int(werte.get('rcon.port', '25575'))), timeout=timeout)
        self.nr = 1
        self._senden(3, werte['rcon.password'])
        if self._lesen()[0] == -1:
            sys.exit('RCON-Kennwort abgelehnt')

    def _senden(self, art, text):
        rumpf = struct.pack('<ii', self.nr, art) + text.encode('utf-8') + b'\x00\x00'
        self.s.sendall(struct.pack('<i', len(rumpf)) + rumpf)
        self.nr += 1

    def _lesen(self):
        laenge = struct.unpack('<i', self._genau(4))[0]
        daten = self._genau(laenge)
        nr, _ = struct.unpack('<ii', daten[:8])
        return nr, daten[8:-2].decode('utf-8', 'replace')

    def _genau(self, n):
        daten = b''
        while len(daten) < n:
            stueck = self.s.recv(n - len(daten))
            if not stueck:
                raise ConnectionError('RCON-Verbindung getrennt')
            daten += stueck
        return daten

    def befehl(self, text):
        self._senden(2, text)
        return self._lesen()[1]

    def close(self):
        self.s.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

# ---------------------------------------------------------------- NBT und Regionsdateien

def _genau(f, n):
    b = f.read(n)
    if len(b) != n:
        raise EOFError
    return b


def _tag(f, t):
    if t == 1: return struct.unpack('>b', _genau(f, 1))[0]
    if t == 2: return struct.unpack('>h', _genau(f, 2))[0]
    if t == 3: return struct.unpack('>i', _genau(f, 4))[0]
    if t == 4: return struct.unpack('>q', _genau(f, 8))[0]
    if t == 5: return struct.unpack('>f', _genau(f, 4))[0]
    if t == 6: return struct.unpack('>d', _genau(f, 8))[0]
    if t == 7:
        n = struct.unpack('>i', _genau(f, 4))[0]
        return _genau(f, n)
    if t == 8:
        n = struct.unpack('>H', _genau(f, 2))[0]
        return _genau(f, n).decode('utf-8', 'replace')
    if t == 9:
        et = _genau(f, 1)[0]
        n = struct.unpack('>i', _genau(f, 4))[0]
        return [_tag(f, et) for _ in range(n)]
    if t == 10:
        d = {}
        while True:
            et = _genau(f, 1)[0]
            if et == 0:
                return d
            nl = struct.unpack('>H', _genau(f, 2))[0]
            schluessel = _genau(f, nl).decode('utf-8', 'replace')  # vor dem Wert lesen
            d[schluessel] = _tag(f, et)
    if t == 11:
        n = struct.unpack('>i', _genau(f, 4))[0]
        return list(struct.unpack('>%di' % n, _genau(f, 4 * n)))
    if t == 12:
        n = struct.unpack('>i', _genau(f, 4))[0]
        return list(struct.unpack('>%dq' % n, _genau(f, 8 * n)))
    raise ValueError(f'unbekannter NBT-Typ {t}')


def nbt(daten):
    """Liest ein unkomprimiertes NBT-Wurzelobjekt."""
    f = io.BytesIO(daten)
    t = _genau(f, 1)[0]
    nl = struct.unpack('>H', _genau(f, 2))[0]
    _genau(f, nl)
    return _tag(f, t)


def nbt_datei(pfad):
    """Liest eine gzip-NBT-Datei (level.dat, Spielerdaten)."""
    import gzip
    with gzip.open(pfad) as f:
        return nbt(f.read())


def region_verzeichnis(server, dimension='minecraft:overworld'):
    """Regionsordner einer Dimension, für das Format ab 26.x und das ältere."""
    welt = welt_verzeichnis(server)
    ns, name = dimension.split(':', 1) if ':' in dimension else ('minecraft', dimension)
    neu = os.path.join(welt, 'dimensions', ns, name, 'region')
    if os.path.isdir(neu):
        return neu
    alt = {'minecraft:overworld': 'region', 'minecraft:the_nether': 'DIM-1/region',
           'minecraft:the_end': 'DIM1/region'}.get(f'{ns}:{name}', f'dimensions/{ns}/{name}/region')
    return os.path.join(welt, alt)


LUFT = ('minecraft:air', 'minecraft:cave_air', 'minecraft:void_air')


class Welt:
    """Liest Blöcke direkt aus den Regionsdateien (nur lesen, auch bei laufendem Server)."""

    def __init__(self, region):
        self.region = region
        self.cache = {}

    def chunk(self, cx, cz):
        """Rohdaten eines Chunks oder None, wenn er nicht erzeugt ist."""
        schluessel = ('roh', cx, cz)
        if schluessel in self.cache:
            return self.cache[schluessel]
        datei = os.path.join(self.region, f'r.{cx >> 5}.{cz >> 5}.mca')
        ergebnis = None
        if os.path.exists(datei):
            with open(datei, 'rb') as f:
                f.seek(4 * ((cx & 31) + (cz & 31) * 32))
                versatz = int.from_bytes(f.read(3), 'big')
                if versatz:
                    f.seek(versatz * 4096)
                    laenge = struct.unpack('>i', f.read(4))[0]
                    art = f.read(1)[0]
                    roh = f.read(laenge - 1)
                    try:
                        ergebnis = nbt(zlib.decompress(roh) if art == 2 else roh)
                    except Exception:
                        ergebnis = None
        self.cache[schluessel] = ergebnis
        return ergebnis

    def _abschnitte(self, cx, cz):
        schluessel = ('abschnitte', cx, cz)
        if schluessel in self.cache:
            return self.cache[schluessel]
        chunk = self.chunk(cx, cz)
        abschnitte = None
        if chunk is not None:
            abschnitte = {}
            for s in chunk.get('sections', []):
                bs = s.get('block_states') or {}
                palette = []
                for p in bs.get('palette', []):
                    eig = p.get('Properties') or {}
                    palette.append(p['Name'] + ('[' + ','.join(f'{a}={b}' for a, b in sorted(eig.items())) + ']' if eig else ''))
                if palette:
                    daten = [v & 0xFFFFFFFFFFFFFFFF for v in bs['data']] if bs.get('data') else None
                    abschnitte[s['Y']] = (palette, daten)
        self.cache[schluessel] = abschnitte
        return abschnitte

    def block(self, x, y, z):
        """Block mit Eigenschaften, z. B. 'minecraft:water[level=0]'; None = Chunk nicht erzeugt."""
        abschnitte = self._abschnitte(x >> 4, z >> 4)
        if abschnitte is None:
            return None
        s = abschnitte.get(y >> 4)
        if not s:
            return 'minecraft:air'
        palette, daten = s
        if daten is None:
            return palette[0]
        bits = max(4, (len(palette) - 1).bit_length())
        je = 64 // bits
        i = (y & 15) * 256 + (z & 15) * 16 + (x & 15)
        return palette[(daten[i // je] >> ((i % je) * bits)) & ((1 << bits) - 1)]

    def block_entities(self, cx, cz):
        chunk = self.chunk(cx, cz)
        return (chunk or {}).get('block_entities', []) or []


def name(block):
    """'minecraft:water[level=0]' -> 'minecraft:water'"""
    return block.split('[')[0] if block else block

# ---------------------------------------------------------------- Bauen

class Bau:
    """Sammelt fill/setblock/summon-Befehle und merkt sich die Fläche, die geladen sein muss."""

    def __init__(self):
        self.befehle = []
        self.x1 = self.z1 = 10 ** 9
        self.x2 = self.z2 = -10 ** 9

    def _flaeche(self, *xz):
        for x, z in xz:
            self.x1, self.x2 = min(self.x1, x), max(self.x2, x)
            self.z1, self.z2 = min(self.z1, z), max(self.z2, z)

    def fill(self, x1, y1, z1, x2, y2, z2, block, ersetzt=''):
        self._flaeche((x1, z1), (x2, z2))
        # fill darf höchstens 32768 Blöcke auf einmal setzen: große Quader werden in Scheiben geteilt
        hoehe = abs(y2 - y1) + 1
        breite = (abs(x2 - x1) + 1) * (abs(z2 - z1) + 1)
        if breite * hoehe > 32768:
            schicht = max(1, 32768 // breite)
            unten, oben = min(y1, y2), max(y1, y2)
            for y in range(unten, oben + 1, schicht):
                self.fill(x1, y, z1, x2, min(oben, y + schicht - 1), z2, block, ersetzt)
            return
        self.befehle.append(f'fill {x1} {y1} {z1} {x2} {y2} {z2} {block}' + (f' replace {ersetzt}' if ersetzt else ''))

    def setblock(self, x, y, z, block):
        self._flaeche((x, z))
        self.befehle.append(f'setblock {x} {y} {z} {block}')

    def befehl(self, text, *xz):
        if xz:
            self._flaeche(*xz)
        self.befehle.append(text)

    def mit_forceload(self):
        """Befehle samt forceload add/remove, damit auch Chunks fern von Spielern gesetzt werden."""
        if self.x1 > self.x2:
            return list(self.befehle)
        laden = []
        for cx in range(self.x1 >> 4, (self.x2 >> 4) + 1, 16):
            for cz in range(self.z1 >> 4, (self.z2 >> 4) + 1, 16):
                bx2 = min(self.x2 >> 4, cx + 15)
                bz2 = min(self.z2 >> 4, cz + 15)
                laden.append(f'{cx * 16} {cz * 16} {bx2 * 16 + 15} {bz2 * 16 + 15}')
        return ([f'forceload add {b}' for b in laden] + ['sleep 8'] + self.befehle
                + ['sleep 3'] + [f'forceload remove {b}' for b in laden])


def bau_parser(beschreibung):
    p = argparse.ArgumentParser(description=beschreibung)
    p.add_argument('--server', help='Server-Verzeichnis (sonst MC_DIR oder aktuelles Verzeichnis)')
    p.add_argument('--senden', action='store_true', help='per RCON an den laufenden Server schicken')
    p.add_argument('-o', '--ausgabe', help='Befehle in diese Datei schreiben (sonst auf die Standardausgabe)')
    return p


def ausgeben(bau, args):
    """Schreibt die Befehle aus oder schickt sie per RCON; vorher die Regionsdateien sichern!"""
    zeilen = bau.mit_forceload()
    if args.senden:
        ausfuehren(server_verzeichnis(args.server), zeilen)
        return
    text = '\n'.join(zeilen) + '\n'
    if args.ausgabe:
        with open(args.ausgabe, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'{len(bau.befehle)} Befehle nach {args.ausgabe}', file=sys.stderr)
    else:
        sys.stdout.write(text)


def ausfuehren(server, zeilen, still=('Successfully filled', 'Changed the block', 'Summoned new', 'No blocks were filled')):
    """Führt Befehlszeilen aus; 'sleep N' pausiert, '#' ist Kommentar. Zeigt nur auffällige Antworten."""
    with Rcon(server) as rcon:
        for zeile in zeilen:
            zeile = zeile.strip()
            if not zeile or zeile.startswith('#'):
                continue
            if zeile.startswith('sleep '):
                time.sleep(float(zeile.split()[1]))
                continue
            antwort = rcon.befehl(zeile)
            if antwort and not antwort.startswith(still):
                print(f'> {zeile[:70]} | {antwort[:200]}')


def punkt(text):
    """'10 64 -20' oder '10,64,-20' -> (10, 64, -20)"""
    werte = [int(v) for v in text.replace(',', ' ').split()]
    return tuple(werte)


class Versatz:
    """Baut relativ zu einem Ursprung: fill/setblock nehmen Koordinaten ab (0, 0, 0) = Ursprung."""

    def __init__(self, bau, x, y, z):
        self.bau, self.x, self.y, self.z = bau, x, y, z

    def fill(self, x1, y1, z1, x2, y2, z2, block, ersetzt=''):
        self.bau.fill(self.x + x1, self.y + y1, self.z + z1, self.x + x2, self.y + y2, self.z + z2, block, ersetzt)

    def setblock(self, x, y, z, block):
        self.bau.setblock(self.x + x, self.y + y, self.z + z, block)

    def absolut(self, x, y, z):
        return self.x + x, self.y + y, self.z + z


def text(s):
    """Text für SNBT/JSON in doppelten Anführungszeichen."""
    return s.replace('\\', '\\\\').replace('"', '\\"')
