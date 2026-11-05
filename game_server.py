import socket
import threading
import json
import time
import uuid

# Configuration
HOST = '0.0.0.0'
PORT = 5555
MASTER_HOST = '127.0.0.1'
MASTER_PORT = 5000
SERVER_NAME = "Galactic Sector-7"

class GameServer:
    def __init__(self):
        self.server_id = str(uuid.uuid4())[:8]
        self.clients = {}  # {socket: player_id}
        self.game_state = {} # {player_id: {"name": name, "x": 0, "y": 0, "guild": "None"}}
        self.lock = threading.Lock()
        self.running = True

    def heartbeat(self):
        """Registers this server with the Master Server every 15 seconds."""
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((MASTER_HOST, MASTER_PORT))
                    reg_msg = json.dumps({
                        "type": "REGISTER",
                        "id": self.server_id,
                        "name": SERVER_NAME,
                        "port": PORT
                    })
                    s.sendall(reg_msg.encode('utf-8'))
            except Exception as e:
                print(f"[MASTER] Heartbeat failed: {e}")
            time.sleep(15)

    def handle_client(self, conn, addr):
        player_id = None
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data: return
            
            msg = json.loads(data)
            if msg.get("type") == "JOIN":
                player_id = f"P_{addr[1]}"
                name = msg.get("name", "Unknown")
                with self.lock:
                    self.clients[conn] = player_id
                    self.game_state[player_id] = {"name": name, "x": 500, "y": 500, "guild": "None"}
                conn.sendall(json.dumps({"type": "WELCOME", "id": player_id}).encode('utf-8'))

            while self.running:
                data = conn.recv(1024).decode('utf-8')
                if not data: break
                
                msg = json.loads(data)
                m_type = msg.get("type")
                
                with self.lock:
                    if m_type == "MOVE":
                        if player_id in self.game_state:
                            self.game_state[player_id]["x"] += msg.get("dx", 0)
                            self.game_state[player_id]["y"] += msg.get("dy", 0)
                    elif m_type == "GUILD_JOIN":
                        guild_name = msg.get("guild", "None")
                        if player_id in self.game_state:
                            self.game_state[player_id]["guild"] = guild_name
                    elif m_type == "CHAT":
                        self.broadcast({"type": "CHAT", "sender": player_id, "text": msg.get("text", ""), "guild": self.game_state.get(player_id, {}).get("guild", "None")})

        except Exception as e:
            print(f"[ERROR] {addr} error: {e}")
        finally:
            with self.lock:
                if conn in self.clients:
                    pid = self.clients[conn]
                    del self.clients[conn]
                    if pid in self.game_state: del self.game_state[pid]
            conn.close()

    def broadcast(self, message):
        data = json.dumps(message).encode('utf-8')
        with self.lock:
            for conn in list(self.clients.keys()):
                try: conn.sendall(data)
                except: pass

    def state_broadcaster(self):
        while self.running:
            with self.lock:
                state_msg = {"type": "STATE", "players": self.game_state}
            self.broadcast(state_msg)
            time.sleep(0.1)

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[GAME] Server {SERVER_NAME} running on {PORT}...")
        
        threading.Thread(target=self.heartbeat, daemon=True).start()
        threading.Thread(target=self.state_broadcaster, daemon=True).start()
        
        try:
            while self.running:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            self.running = False
        finally:
            server.close()

if __name__ == "__main__":
    GameServer().start()
