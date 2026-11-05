import socket
import json
import threading
import sys

MASTER_HOST = '127.0.0.1'
MASTER_PORT = 5000

def get_server_list():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((MASTER_HOST, MASTER_PORT))
            s.sendall(json.dumps({"type": "LIST"}).encode('utf-8'))
            data = s.recv(4096).decode('utf-8')
            res = json.loads(data)
            return res.get("servers", [])
    except Exception as e:
        print(f"Error fetching server list: {e}")
        return []

def listen_for_messages(sock):
    while True:
        try:
            data = sock.recv(4096).decode('utf-8')
            if not data: break
            msg = json.loads(data)
            if msg.get("type") == "STATE":
                players = msg.get("players", {})
                # Simplified display: Name [Guild] (x,y)
                info = " | ".join([f"{p['name']} [{p['guild']}]({p['x']},{p['y']})" for p in players.values()])
                print(f"\r[GAME] {info}", end="")
            elif msg.get("type") == "CHAT":
                p = msg.get("sender")
                g = msg.get("guild")
                t = msg.get("text")
                print(f"\n[CHAT] {p} ({g}): {t}")
        except: break

def run_client():
    print("Connecting to Master Registry...")
    servers = get_server_list()
    if not servers:
        print("No active game servers found.")
        return

    print("\nActive Servers:")
    for i, s in enumerate(servers):
        print(f"{i}) {s['name']} - {s['ip']}:{s['port']} (ID: {s['id']})")
    
    try:
        choice = int(input("\nSelect server number to join: "))
        selected = servers[choice]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    name = input("Enter Pilot Name: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((selected['ip'], selected['port']))
    except Exception as e:
        print(f"Could not connect: {e}")
        return

    sock.sendall(json.dumps({"type": "JOIN", "name": name}).encode('utf-8'))
    threading.Thread(target=listen_for_messages, args=(sock,), daemon=True).start()

    print("\nConnected! Controls:\n(W/A/S/D) Move | (G) Join Guild | (C) Chat | (Q) Quit")
    while True:
        cmd = input().lower()
        if cmd == 'w': sock.sendall(json.dumps({"type": "MOVE", "dx": 0, "dy": -10}).encode('utf-8'))
        elif cmd == 's': sock.sendall(json.dumps({"type": "MOVE", "dx": 0, "dy": 10}).encode('utf-8'))
        elif cmd == 'a': sock.sendall(json.dumps({"type": "MOVE", "dx": -10, "dy": 0}).encode('utf-8'))
        elif cmd == 'd': sock.sendall(json.dumps({"type": "MOVE", "dx": 10, "dy": 0}).encode('utf-8'))
        elif cmd == 'g':
            gn = input("Enter Guild Name: ")
            sock.sendall(json.dumps({"type": "GUILD_JOIN", "guild": gn}).encode('utf-8'))
        elif cmd == 'c':
            text = input("Message: ")
            sock.sendall(json.dumps({"type": "CHAT", "text": text}).encode('utf-8'))
        elif cmd == 'q': break

    sock.close()

if __name__ == "__main__":
    run_client()
