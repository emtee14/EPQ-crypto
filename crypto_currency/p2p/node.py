import hashlib
import socket
import threading
import time
from typing import Dict, List

from p2p.connection import Connection


class Node(threading.Thread):
    def __init__(self, host, port, callback, bootstrap,
                 max_connections, log_func) -> None:
        super(Node, self).__init__()

        self.terminate_flag = threading.Event()
        self.host = host
        self.port = port
        self.callback = callback
        self.max_connections = max_connections
        self.log_func = log_func

        self.inbound = []
        self.outbound = []
        self.connect_list = bootstrap

        self.id = hashlib.sha256((str(host)+str(port)+str(time.time())
                                  ).encode("UTF-8")).hexdigest()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.message_recv = 0
        self.message_send = 0

    def log(self, event, event_type):
        log_msg = f"{time.time()} | node.py | {event_type} - {event}"
        self.log_func(log_msg)

    @property
    def total_nodes(self):
        return self.inbound + self.outbound

    @property
    def client_tuples(self):
        temp = []
        for i in self.outbound:
            temp.append((i.host, i.port))
        for i in self.inbound:
            temp.append((i.act_host[0], i.act_host[1]))
        return temp

    def init_sock(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(5.0)
        self.sock.listen(10)
        self.log("Initialised Socket", "INFO")

    def send_all(self, msg: Dict, exclude: List = []):
        connections = self.total_nodes
        for conn in connections:
            if conn.uid not in exclude:
                conn.send(msg)
        self.log("Sent Message to All", "INFO")

    def send(self, conn_id, msg):
        try:
            conn = self.total_nodes.index(conn_id)
        except ValueError:
            self.log("Invalid node id or node disconnected", "ERROR")
        conn.send(msg)

    def create_conn(self, sock, host, port, client):
        return Connection(self, sock, host, port, client, self.log)

    def connect_node(self, host, port):
        if host == self.host and port == self.port:
            return 1  # Tried to connect to self

        for node in self.total_nodes:
            if host == node.host and port == node.port:
                return 1
        try:
            if (self.max_connections == 0 or len(self.total_nodes) < self.max_connections):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))

                client_thread = self.create_conn(sock, host, port, True)
                client_thread.start()
                while client_thread.uid is None:
                    time.sleep(0.01)
                connected = False
                for connection in self.total_nodes:
                    if connection.uid == client_thread.uid:
                        connected = True
                        break
                if connected is False:
                    self.outbound.append(client_thread)
                    self.log(f"New Client Connected {host}:{port}", "INFO")
                    return 3
                else:
                    client_thread.stop()
            else:
                self.log("Too many clients", "ERROR")
        except Exception as e:
            print("Unable to connect", e)
            return 2

    def reconnect_nodes(self):
        self.connect_list = list(
                                 set([(i[0], i[1]) for i in self.connect_list])
                                 )
        for node in self.connect_list:
            connected = False
            for client in self.outbound:
                if client.port == node[1] and client.host == node[0]:
                    connected = True
                    break
            if not connected:
                if self.connect_node(node[0], node[1]) in [1, 3]:
                    self.connect_list.remove(node)

    def disconnected_node(self, conn):
        if conn in self.inbound:
            self.inbound.remove(conn)
        elif conn in self.outbound:
            self.outbound.remove(conn)

    def stop(self):
        self.terminate_flag.set()

    def run(self):
        self.init_sock()
        self.log("Node Starting", "INFO")
        while not self.terminate_flag.is_set():
            try:
                conn, addr = self.sock.accept()
                if self.max_connections == 0 or len(self.total_nodes) < self.max_connections:
                    conn_thread = self.create_conn(conn, addr[0],
                                                   addr[1], False)
                    conn_thread.start()
                    while conn_thread.uid is None:
                        time.sleep(0.01)
                    connected = False
                    for connection in self.total_nodes:
                        if connection.uid == conn_thread.uid:
                            connected = True
                            break
                    if connected is False:
                        self.inbound.append(conn_thread)
                        self.log(f"New Client Connected {addr[0]}:{addr[1]}",
                                 "INFO")
                    else:
                        conn_thread.stop()
                else:
                    conn.close()
            except socket.timeout:
                pass
            self.reconnect_nodes()
            time.sleep(0.01)

        self.log("Shutting Down", "INFO")
        for thread in self.inbound:
            thread.stop()
        for thread in self.outbound:
            thread.stop()

        for thread in self.inbound:
            thread.join()
        for thread in self.outbound:
            thread.join()

        self.sock.shutdown(2)
        self.sock.close()
