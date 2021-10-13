import socket

class Server():
    def __init__(self) -> None:
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_server.bind(("0.0.0.0", 14605))