from blockchain.transaction import Transaction
from blockchain.block import Block
from blockchain.blockchain import Blockchain
from p2p.node import Node

"""
msg format
{
    "type": "transaction, block, heartbear",
    "data": {"data pertaining to the message"},
    "node_id": "sender nodeid"
}
"""


class Handler():
    def __init__(self, msg, blockchain: Blockchain, node: Node, log) -> None:
        self.msg = msg
        self.log = log
        self.blockchain = Blockchain(self.log, blockchain)
        self.node = node
        self.parse_msg()

    def add_transaction(self):
        tran = self.msg["data"]
        tran_obj = Transaction(tran["sender"], tran["receiver"], tran["value"],
                               tran["data"], tran["fee"], tran["signature"],
                               tran["nonce"])
        tran_obj.verify_signature()
        if tran_obj.valid is True:
            if self.blockchain.add_to_mempool(tran):
                new_msg = self.msg.copy()
                new_msg["node_id"] = self.node.id
                self.node.send_all(new_msg, exclude=[self.msg["node_id"]])
            return True
        else:
            self.log("handler.py", "ERORR", "Invalid transaction")
            return False  # Invalid transaction received

    def add_block(self):
        block = self.msg["data"]
        transaction_dicts = self.msg["data"]["transactions"]
        transactions = []
        for tran in transaction_dicts:
            tran_obj = Transaction(tran["sender"], tran["receiver"],
                                   tran["value"], tran["data"], tran["fee"],
                                   tran["signature"], tran["nonce"])
            tran_obj.verify_signature()
            transactions.append(tuple(tran_obj))
        block_obj = Block(block["parent_block"], block["timestamp"],
                          transactions,
                          block["hash"], block["nonce"], block["coinbase"])
        if block_obj.verify() is True:
            try:
                self.blockchain.add_block(block_obj)
                new_msg = self.msg.copy()
                new_msg["node_id"] = self.node.id
                self.node.send_all(new_msg, exclude=[self.msg["node_id"]])
                return True
            except ValueError:
                return False
        else:
            return False  # Invalid Block

    def disconnect(self):
        for conn in self.node.total_nodes:
            if conn.id == self.msg["node_id"]:
                conn.stop()
                if conn in self.node.inbound:
                    self.node.inbound.remove(conn)
                elif conn in self.node.outbound:
                    self.node.outbound.remove(conn)

    def parse_msg(self):
        match self.msg["type"]:
            case "add_transaction":
                self.add_transaction()
                self.log("handler.py", "INFO", "New transaction received")
            case "new_block":
                self.add_block()
                self.log("handler.py", "INFO", "New block received")
            case "disconnect":
                self.disconnect()
