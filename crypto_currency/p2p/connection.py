import socket
import threading
import json
import time


class Connection(threading.Thread):
    def __init__(self, parent_proc, sock_obj, host, port, client,
                 log_func) -> None:
        super(Connection, self).__init__()
        self.parent_proc = parent_proc
        self._stop_event = threading.Event()
        self.client = client  # True if connecting to another server
        self.sock = sock_obj
        self.uid = None
        self.host = host
        self.port = port
        self.EOT_CHAR = 0x14.to_bytes(1, 'big')
        self.sock.settimeout(15)
        self.ping_pong()
        self.log = log_func

    def __str__(self):
        return f"{self.host}:{self.port} {self.uid[:8]}"

    def send(self, data: dict):
        try:
            msg_str = json.dumps(data, sort_keys=True)
        except Exception:
            raise ValueError("Invalid dict unable to convert to string")
        msg_bytes = msg_str.encode("UTF-8") + self.EOT_CHAR
        self.sock.sendall(msg_bytes)

    def parse_message(self, msg: bytes) -> dict:
        json_str = msg.decode("UTF-8")
        try:
            msg_dict = json.loads(json_str)
        except Exception:
            raise ValueError("Invalid message cannot convert to dict")
        return msg_dict

    def handle_msg(self, msg):
        self.parent_proc.callback(msg)

    def stop(self):
        self._stop_event.set()

    def run(self):
        buffer = b""
        while not self._stop_event.is_set():
            transmission = b""
            try:
                transmission = self.sock.recv(4096)
            except socket.timeout:
                pass
            except Exception:
                self.stop()
            if transmission != b"":
                buffer += transmission
                eot_pos = buffer.find(self.EOT_CHAR)
                while eot_pos > 0:
                    msg_bytes = buffer[:eot_pos]
                    buffer = buffer[eot_pos+1:]
                    try:
                        msg_dict = self.parse_message(msg_bytes)
                        self.handle_msg(msg_dict)
                    except ValueError:
                        self.log("Error handling or parsing message", "ERROR")
                    eot_pos = buffer.find(self.EOT_CHAR)
            time.sleep(0.05)
        self.send({
            "type": "disconnect",
            "data": {},
            "node_id": self.parent_proc.id
        })
        try:
            self.sock.settimeout(None)
            self.sock.shutdown(2)
            self.sock.close()
        except OSError as e:
            if str(e) != "[Errno 57] Socket is not connected":
                print(e)
                raise e
        self.parent_proc.disconnected_node(self)
        self.log(f"Client disconnected {self.host}:{self.port}",
                 "INFO")
        # loggin stuff

    def ping_pong(self):
        if self.client:
            self.send({
                "type": "init_ping",
                "data": {
                    "id": self.parent_proc.id,
                    "clients": self.parent_proc.client_tuples,
                    "act_host": (self.parent_proc.host, self.parent_proc.port)
                    }
                })
        full_msg = False
        buffer = b""
        while not full_msg:
            data = b""
            data = self.sock.recv(4096)
            if data != b"":
                buffer += data
                eot_pos = buffer.find(self.EOT_CHAR)
                if eot_pos != -1:
                    msg_bytes = buffer[:eot_pos]
                    msg = self.parse_message(msg_bytes)
                    break
        self.parent_proc.connect_list += [(i[0], i[1]) for i in msg["data"]["clients"]]
        self.uid = msg["data"]["id"]
        self.act_host = msg["data"]["act_host"]
        if msg["type"] == "init_ping":
            self.send({
                "type": "resp_pong",
                "data": {
                    "id": self.parent_proc.id,
                    "clients": self.parent_proc.client_tuples,
                    "act_host": (self.parent_proc.host, self.parent_proc.port)
                    }
                })
