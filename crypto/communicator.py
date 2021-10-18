import socket
import json
from queue import Queue
from threading import Event
import time


def connect_server(host: str, port: int) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return (s, host)


class socketObject():
    def __init__(self, conn: socket.socket, addr: str) -> None:
        self.conn = conn
        self.addr = addr
        self.msg_history = []

    def log_msg(self, msg):
        log_record = {
            "timestamp": time.time(),
            "message": msg
        }
        self.msg_history.append(log_record)

    def send_msg(self, dict_obj: dict):
        try:
            msg = json.dumps(dict_obj)
        except TypeError:
            print("Failed to send message unable to serialize dict")
            return
        self.log_msg(msg)
        self.conn.send(hex(len(msg))[2:].zfill(4).encode("UTF-8"))
        self.conn.send(msg.encode("UTF-8"))

    def get_msg(self):
        length = self.conn.recv(4).decode()
        serialized_msg = self.conn.recv(int(length, base=16)).decode()
        msg = json.loads(serialized_msg)
        return msg


class socketHandler():
    def __init__(self, conn: socketObject, main_queue: Queue,
                 peer_list: Queue, quitEvent: Event, client=False) -> None:
        # if client is true it means this object was called by server
        self.client = client
        self.conn = conn
        self.main_queue = main_queue
        self.peer_list = peer_list
        self.connected = False
        self.quitEvent = quitEvent
        self.init_conn()
        self.get_peers()

    def init_conn(self) -> None:
        """Sends ping message to client or pong to server to check connection
        """
        if self.client:
            self.conn.send_msg({"command": "PING"})
        resp = self.conn.get_msg()
        if resp["command"] == "PING":
            self.conn.send_msg({"command": "PONG"})
            self.connected = True
        elif resp["command"] == "PONG":
            self.connected = True

    def get_peers(self):
        if not self.client:
            self.conn.send_msg({"command": "PEERS"})
            peers = self.conn.get_msg()
            if peers["command"] == "PEERS":
                for peer in peers["peers"]:
                    self.peer_list.put(peer)

    def handler(self):
        while not self.quitEvent.isSet():
            msg_len = int(self.conn.recv(4).decode("UTF-8"), 16)
            msg_string = self.conn.recv(msg_len).decode("UTF-8")
            msg = json.loads(msg_string)
            return msg
