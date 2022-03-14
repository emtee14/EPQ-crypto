from p2p.node import Node
from web_api import main
from handler import Handler
from datetime import datetime
import atexit
import os
from blockchain.blockchain import Blockchain
from miner import minerAgent


class cryptoNode():
    def __init__(self, host="0.0.0.0", port=14065,
                 bootstrap=[("crypto.morgan-thomas.co.uk", 14065),
                            ("crypto.morgan-thomas.co.uk", 14066),
                            ("crypto.morgan-thomas.co.uk", 14067)],
                 verbose=3, log_file=f"{os.getcwd()}/crypto.log",
                 max_connections=0, blockchain="blockchain.db", api=True,
                 web_port=5555, miner=False, miner_addr=None) -> None:
        self.verbose = verbose
        self.log_file = log_file

        self.web_api = api
        self.web_port = web_port

        self.miner = miner
        self.miner_addr = miner_addr

        if self.web_api and self.miner:
            raise ValueError("Cannot have miner and web api enabled")

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
        atexit.register(self.stop)
        self.node.start()
        if self.web_api:
            app = main.create_app(self.blockchain, self.node, self.log)
            app.run(port=self.web_port)
        elif self.miner:
            miner = minerAgent(self.blockchain, self.log,
                               self.miner_addr, self.node)
            miner.start()

    def stop(self):
        self.node.stop()
        self.node.join()

    def log(self, event_location, event_type, event):
        log_msg = f"{str(datetime.utcnow())} || {event_type} @ {event_location} > {event}"
        if self.verbose > 1:
            with open(self.log_file, "a") as f:
                f.write(log_msg + "\n")
        if self.verbose > 2:
            print(log_msg)


if __name__ == "__main__":
    server_node = cryptoNode(bootstrap=[])
    server_node.start()
