import hashlib
import socket
import threading
import time
from typing import Dict, List

from connection import Connection


class Node(threading.Thread):
    def __init__(self, host, port, callback, bootstrap,
                 max_connections=0) -> None:
        super(Node, self).__init__()

        self.terminate_flag = threading.Event()
        self.host = host
        self.port = port
        self.callback = callback
        self.max_connections = max_connections

        self.inbound = []
        self.outbound = []
        self.connect_list = bootstrap

        self.id = hashlib.sha256((str(host)+str(port)+str(time.time())
                                  ).encode("UTF-8")).hexdigest()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.message_recv = 0
        self.message_send = 0

    @property
    def total_nodes(self):
        return self.inbound + self.outbound

    @property
    def client_tuples(self):
        temp = []
        for i in self.outbound:
            temp.append((i.host, i.port))
        return temp

    def init_sock(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(5.0)
        self.sock.listen(5)

    def send_all(self, msg: Dict, exclude: List = []):
        connections = self.total_nodes
        for conn in connections:
            if conn.uid not in exclude:
                conn.send(msg)

    def send(self, conn_id, msg):
        try:
            conn = self.total_nodes.index(conn_id)
        except ValueError:
            raise ValueError("Invalid node id or node disconnected")
        conn.send(msg)

    def create_conn(self, sock, host, port, client):
        return Connection(self, sock, host, port, client)

    def connect_node(self, host, port):
        if host == self.host and port == self.port:
            print("Cannot connect to self")
            return False

        for node in self.total_nodes:
            if host == node.host and port == node.port:
                print("Already connected to node")
                return False
        try:
            if (self.max_connections == 0 or len(self.total_nodes) < self.max_connections):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))

                client_thread = self.create_conn(sock, host, port, True)
                client_thread.start()
                self.outbound.append(client_thread)
            else:
                print("Too many clients")
        except Exception as e:
            print("Unable to connect", e)
            print()
            return False

    def reconnect_nodes(self):
        for node in self.connect_list:
            connected = False
            for client in self.outbound:
                if client.port == node[1] and client.host == node[0]:
                    connected = True
                    break
            if not connected:
                self.connect_node(node[0], node[1])
                self.connect_list.remove(node)

    def stop(self):
        self.terminate_flag.set()

    def run(self):
        self.init_sock()
        while not self.terminate_flag.is_set():
            try:
                conn, addr = self.sock.accept()
                if self.max_connections == 0 or len(self.total_nodes) < self.max_connections:
                    conn_thread = self.create_conn(conn, addr[0],
                                                   addr[1], False)
                    conn_thread.start()
                    self.inbound.append(conn_thread)
                else:
                    conn.close()
            except socket.timeout:
                pass
            self.reconnect_nodes()

        for t in self.inbound:
            t.stop()
        for t in self.outbound:
            t.stop()

        time.sleep(1)
        for t in self.inbound:
            t.join()
        for t in self.outbound:
            t.join()
