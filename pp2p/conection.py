import socket
import threading
import json
import time


class Connection(threading.Thread):
    def __init__(self, parent_proc, sock_obj, uid, host, port) -> None:
        super(Connection, self).__init__()
        self.parent_proc = parent_proc
        self.stop = threading.Event()
        self.sock = sock_obj
        self.uid = uid
        self.host = host
        self.port = port
        self.EOT_CHAR = 0x14.to_bytes(1, 'big')
        self.sock.settimeout(15)

    def send(self, data: dict):
        try:
            msg_str = json.dumps(data, sort_keys=True)
        except Exception:
            raise ValueError("Invalid dict unable to convert to string")
        msg_bytes = msg_str.encode("UTF-8") + self.EOT_CHAR
        self.sock.sendall(msg_bytes)

    def parse_message(self, msg: bytes) -> dict:
        json_str = msg.decode("UTF-8")[:-1]
        try:
            msg_dict = json.loads(json_str)
        except Exception:
            raise ValueError("Invalid message cannot convert to dict")
        return msg_dict

    def run(self):
        buffer = b""
        while not self.stop.is_set():
            transmission = b""
            try:
                transmission = self.sock.recv(4096)
            except socket.timeout:
                pass # error loggign
            if transmission != b"":
                buffer += transmission
                eot_position = buffer.find(self.EOT_CHAR)
                while eot_position > 0:
                    msg_bytes = buffer[:eot_position]
                    buffer = buffer[eot_position+1:]
                    try:
                        msg_dict = self.parse_message(msg_bytes)
                        self.parent_proc.message(msg_dict)
                    except ValueError:
                        pass # logging thingy
                    eot_position = buffer.find(self.EOT_CHAR)
            time.sleep(0.05)
        self.sock.settimeout(None)
        self.sock.close()
        self.parent_proc.disconnected_node(self)
        # loggin stuff

# https://github.com/macsnoeren/python-p2p-network/blob/development/p2pnetwork/nodeconnection.py
