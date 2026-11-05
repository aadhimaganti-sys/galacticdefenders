import socket
import threading
import json
import time

# Master Server Configuration
HOST = '0.0.0.0'
PORT = 5000

class MasterServer:
    def __init__(self):
        self.servers = {}  # {server_id: {"ip": ip, "port": port, "name": name, "last_seen": time}}
        self.lock = threading.Lock()
        self.running = True

    def handle_request(self, conn, addr):
        try:
            data = conn.recv(1024).decode('utf-8')
            if not data:
                return
            
            msg = json.loads(data)
            msg_type = msg.get("type")

            if msg_type == "REGISTER":
                # Game server announcing itself
                s_id = msg.get("id")
                with self.lock:
                    self.servers[s_id] = {
                        "ip": addr[0],
                        "port": msg.get("port"),
                        "name": msg.get("name", "Unknown Server"),
                        "last_seen": time.time()
                    }
                conn.sendall(json.dumps({"type": "REG_OK"}).encode('utf-8'))

            elif msg_type == "LIST":
                # Client requesting list of servers
                with self.lock:
                    # Clean up stale servers (older than 30s)
                    now = time.time()
                    self.servers = {sid: s for sid, s in self.servers.items() if now - s["last_seen"] < 30}
                    server_list = [{"id": sid, **info} for sid, info in self.servers.items()]
                conn.sendall(json.dumps({"type": "SERVER_LIST", "servers": server_list}).encode('utf-8'))

        except Exception as e:
            print(f"[ERROR] Master request error from {addr}: {e}")
        finally:
            conn.close()

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[MASTER] Global Registry listening on {HOST}:{PORT}...")
        
        try:
            while self.running:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_request, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            self.running = False
        finally:
            server.close()

if __name__ == "__main__":
    MasterServer().start()
