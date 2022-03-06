from p2p.node import Node
from web_api import main
from handler import Handler
import atexit
import os
from blockchain.blockchain import Blockchain


class cryptoNode():
    def __init__(self, host="0.0.0.0", port=14065,
                 bootstrap=[("crypto.morgan-thomas.co.uk", 14065),
                            ("crypto.morgan-thomas.co.uk", 14066),
                            ("crypto.morgan-thomas.co.uk", 14067)],
                 verbose=3, log_file=f"{os.getcwd()}/crypto.log",
                 max_connections=0, blockchain="blockchain.db") -> None:
        self.verbose = verbose
        self.log_file = log_file
        self.node = Node(host, port, self.handler, bootstrap, max_connections,
                         self.log)
        self.blockchain = blockchain
        self.init_blockchain()

    def init_blockchain(self):
        blockchain = Blockchain(self.log)
        blockchain.flush_mempool()

    def handler(self, msg) -> None:
        Handler(msg, self.blockchain, self.node, self.log)

    def start(self):
        self.node.start()
        app = main.create_app(self.blockchain, self.node)
        app.run(debug=True, port=5555)

    def stop(self):
        self.node.stop()
        self.node.join()

    def log(self, log_msg):
        if self.verbose > 1:
            with open(self.log_file, "a") as f:
                f.write(log_msg + "\n")
        if self.verbose > 2:
            print(log_msg)


if __name__ == "__main__":
    server_node = cryptoNode(bootstrap=[])
    atexit.register(server_node.stop)
    server_node.start()
