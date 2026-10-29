#!/usr/bin/env python3
# Autor: Dschonas04 (https://github.com/Dschonas04)
# Brücke zwischen dem Chat eines Minecraft-Servers und einer Telegram-Gruppe.
# Umgebung: TG_TOKEN (Bot-Token), MC_DIR (Server-Verzeichnis), optional MC_NAME (Anzeigename),
# STATE_DIR (Zustand: Chat-ID, Update-Stand). Den Bot in die Gruppe einladen; die erste Gruppe wird verbunden.
import json, os, re, socket, struct, threading, time, urllib.request, urllib.parse

MC = os.environ.get('MC_DIR', '/srv/minecraft')
LOG = MC + '/logs/latest.log'
STATE = os.environ.get('STATE_DIR', '/var/lib/mc-telegram')
SERVER = os.environ.get('MC_NAME', 'dem Minecraft-Server')
API = 'https://api.telegram.org/bot' + os.environ['TG_TOKEN'] + '/'
# Ranglisten-Teams schreiben z. B. '1. Name  12 Tode': nur dieses Muster (Platz vorn, Zahl + Wort hinten)
# wird übersprungen. Freier Text davor ist nicht erlaubt, sonst ließen sich mit /say oder /me
# ("[Bob] Steve joined the game") falsche Beitritts- oder Chatmeldungen erzeugen.
NAME = r'(?:\d{1,3}\.\s+)?([A-Za-z0-9_]{3,16})(?:\s+\d+\s+\w+)?'
CHAT = re.compile(r'\[Server thread/INFO\]: <' + NAME + r'> (.*)$')
JOIN = re.compile(r'\[Server thread/INFO\]: ' + NAME + r' joined the game$')
LEFT = re.compile(r'\[Server thread/INFO\]: ' + NAME + r' left the game$')
DONE = re.compile(r'\[Server thread/INFO\]: Done \(')
STOP = re.compile(r'\[Server thread/INFO\]: Stopping the server')

def tg(method, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(API + method, data, timeout=70) as r:
        return json.load(r)

def chat_id():
    try: return int(open(STATE + '/chat').read())
    except Exception: return None

def senden(text):
    cid = chat_id()
    if cid is None: return
    for _ in range(3):
        try: tg('sendMessage', chat_id=cid, text=text); return
        except Exception: time.sleep(3)

def rcon(cmd):
    pw = next(l.split('=', 1)[1].strip() for l in open(MC + '/server.properties') if l.startswith('rcon.password='))
    port = int(next((l.split('=', 1)[1] for l in open(MC + '/server.properties') if l.startswith('rcon.port=')), 25575))
    def pkt(rid, typ, body):
        d = struct.pack('<ii', rid, typ) + body.encode() + b'\x00\x00'
        return struct.pack('<i', len(d)) + d
    with socket.create_connection(('127.0.0.1', port), timeout=10) as s:
        s.sendall(pkt(1, 3, pw)); s.recv(4096)
        s.sendall(pkt(2, 2, cmd)); s.recv(4096)

def log_lesen():
    f = None; ino = None
    while True:
        try:
            st = os.stat(LOG)
            if st.st_ino != ino or (f and f.tell() > st.st_size):
                if f: f.close()
                f = open(LOG, encoding='utf-8', errors='replace')
                if ino is None: f.seek(0, 2)
                ino = st.st_ino
            line = f.readline()
            if not line:
                time.sleep(0.5); continue
            line = line.rstrip('\n')
            if m := CHAT.search(line): senden(f'{m[1]}: {m[2]}')
            elif m := JOIN.search(line): senden(f'➕ {m[1]} ist beigetreten')
            elif m := LEFT.search(line): senden(f'➖ {m[1]} hat das Spiel verlassen')
            elif DONE.search(line): senden('🟢 Server ist gestartet')
            elif STOP.search(line): senden('🔴 Server wird gestoppt')
        except FileNotFoundError:
            time.sleep(2)
        except Exception as e:
            print('log:', e, flush=True); time.sleep(2)

def telegram_lesen():
    try: off = int(open(STATE + '/offset').read())
    except Exception: off = 0
    while True:
        try:
            r = tg('getUpdates', offset=off, timeout=50, allowed_updates='["message","my_chat_member"]')
        except Exception as e:
            print('tg:', e, flush=True); time.sleep(5); continue
        for u in r.get('result', []):
            off = u['update_id'] + 1
            open(STATE + '/offset', 'w').write(str(off))
            m = u.get('message') or u.get('my_chat_member') or {}
            c = m.get('chat', {})
            if chat_id() is None and c.get('type') in ('group', 'supergroup'):
                open(STATE + '/chat', 'w').write(str(c['id']))
                senden(f'Verbunden mit {SERVER}. Der Spiel-Chat erscheint hier, Nachrichten von hier gehen ins Spiel.')
                continue
            if c.get('id') != chat_id() or 'message' not in u: continue
            if u['message'].get('migrate_to_chat_id'):  # Gruppe wurde zur Supergruppe
                open(STATE + '/chat', 'w').write(str(u['message']['migrate_to_chat_id'])); continue
            text = u['message'].get('text') or u['message'].get('caption')
            von = u['message'].get('from', {})
            if not text or von.get('is_bot'): continue
            if text.startswith('/'):  # /mc Text klappt auch ohne Gruppen-Lesezugriff
                cmd, _, rest = text.partition(' ')
                if cmd.split('@')[0] != '/mc' or not rest.strip(): continue
                text = rest.strip()
            name = von.get('first_name') or von.get('username') or '?'
            teile = ['', {'text': '[Telegram] ', 'color': 'aqua'}, {'text': name + ': ', 'color': 'aqua'}, {'text': text[:256]}]
            try: rcon('tellraw @a ' + json.dumps(teile, ensure_ascii=False))
            except Exception as e: print('rcon:', e, flush=True)

threading.Thread(target=log_lesen, daemon=True).start()
telegram_lesen()
