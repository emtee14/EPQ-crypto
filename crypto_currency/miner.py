import time

from blockchain.block import Block
from blockchain.blockchain import Blockchain
from blockchain.miner import Miner
from blockchain.transaction import Transaction


class minerAgent():
    def __init__(self, blockchain, log_func, miner_addr, node) -> None:
        self.blockchain = Blockchain(log_func, db=blockchain)
        self.miner_addr = miner_addr
        self.log = log_func
        self.node = node

    def create_block(self, transaction_dicts):
        transaction_dicts = transaction_dicts
        transactions = []
        parent_block = self.blockchain.prev_hash
        for tran in transaction_dicts:
            tran_obj = Transaction(tran["sender"], tran["receiver"],
                                   tran["value"], tran["data"], tran["fee"],
                                   tran["signature"], tran["nonce"])
            transactions.append(tuple(tran_obj))
        proposed_block = Block(parent_block, time.time(), transactions)
        self.log("miner.py", "INFO", "Created block")
        return proposed_block

    def mine_block(self, block: Block):
        miner = Miner(dict(block), "00000", self.miner_addr)
        self.log("miner.py", "INFO", "Started mining block")
        miner.mine_block()
        block.christen(miner.hash, miner.nonce, self.miner_addr)
        self.log("miner.py", "INFO", f"Mined block @ {miner.hash_speed}H/s")
        return block

    def share_block(self, block):
        block_dict = dict(block)
        self.node.send_all(block_dict)

    def start(self):
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if counter == 15:
                counter = 0
                if self.blockchain.mem_pool != []:
                    transactions = self.blockchain.mem_pool
                    proposed_block = self.create_block(transactions)
                    mined_block = self.mine_block(proposed_block)
                    self.blockchain.add_block(mined_block)
                    self.share_block({
                        "type": "new_block",
                        "data": dict(mined_block),
                        "node_id": self.node.id
                    })
