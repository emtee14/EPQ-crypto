import json
import sqlite3
from statistics import mean
from typing import Dict, List

from Crypto.PublicKey import RSA

from blockchain.block import Block


class Blockchain():
    def __init__(self, log_func, db="blockchain.db") -> None:
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.verify_db()
        self.log = log_func

    def verify_db(self) -> None:
        """If tables do not exist in DB they will be created
        """
        self.cur.execute("""SELECT name FROM sqlite_master WHERE type='table'
                            AND name='transactions' OR name='blocks'
                            OR name='mempool';""")
        if not (len(self.cur.fetchall()) == 3):
            self.cur.execute("""CREATE TABLE blocks (hash VARCHAR(64),
                                nonce INT, coinbase VARCHAR(2000),
                                parent_block VARCHAR(64), timestamp INT);""")
            self.cur.execute("""CREATE TABLE transactions (sender VARCHAR(2000),
                             receiver VARCHAR(2000), value INT,
                             data VARCHAR(256), fee INT,
                             signature VARCHAR(512), nonce INT,
                             parent_block VARCHAR(64));""")
            self.cur.execute("""CREATE TABLE mempool
                             (tran VARCHAR(10));""")
            self.conn.commit()

    def get_block(self, block_hash: str) -> Block:
        """Returns a Block object of the desired block containing all it's data

        :param block_hash: The hash for the requested block, defaults to None
        :type block_hash: str
        :return: Block object containing all block data
        :rtype: Block
        """
        self.cur.execute("SELECT * FROM blocks WHERE hash = ?",
                         (block_hash,))
        block_tuple = self.cur.fetchone()
        self.cur.execute("""SELECT sender, receiver, value, data, fee,
                         signature, nonce FROM transactions
                         WHERE parent_block = ?""",
                         (block_tuple[0],))
        transaction_list = self.cur.fetchall()
        block = Block(block_tuple[3], block_tuple[4], transaction_list,
                      block_tuple[0], block_tuple[1], block_tuple[2])
        return block

    def get_balance(self, public_key: str) -> float:
        """Returns account balance of a given account

        :param public_key: Public key to identify account
        :type public_key: str
        :return: Current balance
        :rtype: float
        """
        public_key = RSA.import_key(bytes.fromhex(public_key))
        key_str = public_key.export_key("DER").hex()
        balance = 0.0
        self.cur.execute("""SELECT sender, receiver, value, fee FROM transactions WHERE
                            sender = ? OR receiver = ?""",
                         (key_str, key_str,))
        transactions = self.cur.fetchall()
        for transaction in transactions:
            if transaction[0] == key_str:
                balance -= transaction[2]
                balance -= transaction[3]
            elif transaction[1] == key_str:
                balance += transaction[2]
        self.cur.execute("""SELECT coinbase FROM blocks WHERE coinbase = ?""",
                         (key_str,))
        coinbases = len(self.cur.fetchall())
        balance += coinbases*10
        return balance

    def get_transactions(self, public_key: str) -> Dict:
        """Returns transactions from a specific account

        :param public_key: The public key of the account to get
                           transactions from
        :type public_key: str
        :return: Dictionary containing all the transactions
        :rtype: Dict
        """
        public_key = RSA.import_key(bytes.fromhex(public_key))
        key_str = public_key.export_key("DER").hex()
        self.cur.execute("""SELECT * FROM transactions
                         WHERE sender=? OR receiver = ?""",
                         (key_str, key_str,))
        transaction_tuples = self.cur.fetchall()
        resp = {"account": key_str, "transactions": []}
        for tran in transaction_tuples:
            resp["transactions"].append({
                "sender": tran[0],
                "receiver": tran[1],
                "value": tran[2],
                "data": tran[3],
                "fee": tran[4],
                "signature": tran[5],
                "nonce": tran[6],
                "block": tran[7]
            })
        return resp

    def add_block(self, block: Block) -> None:
        """Validates block and all transactions contained within then adds it
           to blockchain

        :param block: Block object for the block you wish to be added
        :type block: Block
        :raises ValueError: Raises error if there is an error in the validity
        of the block
        """
        if block.verify():
            self.cur.execute("SELECT * FROM blocks;")
            genesis = True if self.cur.fetchone() is None else False
            self.cur.execute("SELECT * FROM blocks WHERE parent_block = ?",
                             (block.parent_block,))
            dupe_block = self.cur.fetchone()
            if dupe_block is not None:
                raise ValueError("Block has already been mined and added")

            if genesis is True or block.parent_block == self.prev_hash:
                for tran in block.transactions:
                    sender_bal = self.get_balance(tran.sender)
                    if (sender_bal < tran.required_value):
                        raise ValueError("Account doesn't have enough funds")
                    if tran.fee != (tran.value*0.05):
                        raise ValueError("Invalid transaction fee")
                block_tuple = (block.hash, block.nonce, block.coinbase,
                               block.parent_block, block.timestamp)
                self.cur.execute("""INSERT INTO blocks (hash, nonce, coinbase, parent_block, timestamp)
                                 VALUES (?, ?, ?, ?, ?);""", block_tuple)
                for tran in block.transactions:
                    tran_tuple = tuple(tran)
                    tran_tuple += (block.hash,)
                    self.cur.execute("""INSERT INTO transactions (sender, receiver, value,
                                     data, fee, signature, nonce, parent_block)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
                                     tran_tuple)
                    signed_tran = {}
                    keys = ["sender", "receiver", "value", "data", "fee",
                            "signature", "nonce"]
                    for idx, i in enumerate(tran_tuple[:-1]):
                        signed_tran[keys[idx]] = i
                    tran_str = json.dumps(signed_tran, sort_keys=True)
                    self.cur.execute("""DELETE FROM mempool WHERE tran = ?""",
                                     (tran_str,))

                self.conn.commit()
                self.log("blockchain.py", "INFO",
                         f"New block added {block.hash}")
            else:
                self.log("blockchain.py", "ERROR", "Invalid parent hash")
                raise ValueError("Invalid Parent Hash")

    @property
    def prev_hash(self) -> str:
        """Returns the hash of the most recent block

        :return: SHA256 hash of most recent block
        :rtype: str
        """
        self.cur.execute("SELECT MAX(timestamp) as max_number FROM blocks;")
        prev_block = self.cur.fetchone()[0]
        if prev_block is not None:
            self.cur.execute("SELECT hash FROM blocks WHERE timestamp = ?",
                             (prev_block,))
            return self.cur.fetchone()[0]
        else:
            return None

    def get_tran_nonce(self, addr: str) -> int:
        """Get the nonce value for transactions from specified account

        :param addr: Address of account to get nonce from
        :type addr: str
        :return: Nonce of account
        :rtype: int
        """
        self.cur.execute("SELECT sender FROM transactions WHERE sender = ?",
                         (addr,))
        try:
            nonce = len(self.cur.fetchall())
        except TypeError:
            nonce = 0
        return nonce

    @property
    def mem_pool(self) -> List:
        """Returns the transactions in the current mempool

        :return: List of all transactions in dictionary form
        :rtype: List
        """
        self.cur.execute("""SELECT * FROM mempool""")
        tran_strings = self.cur.fetchall()
        transactions = []
        for i in tran_strings:
            transactions.append(json.loads(i[0]))
        return transactions

    def add_to_mempool(self, transaction: Dict) -> bool:
        """Adds a transaction to mempool

        :param transaction: Transaction sata
        :type transaction: Dict
        :return: Whether or not it succeeded
        :rtype: bool
        """
        tran_str = json.dumps(transaction, sort_keys=True)
        self.cur.execute("""SELECT * FROM mempool WHERE tran = ?""",
                         (tran_str,))
        if self.cur.fetchone() is None:
            self.cur.execute("""INSERT INTO mempool (tran) VALUES (?);""",
                             (tran_str,))
            self.conn.commit()
            self.log("blockchain.py", "INFO", "Added transaction to mempool")
            return True
        return False

    def flush_mempool(self):
        """Deletes all transactions from mempool
        """
        self.cur.execute("DELETE FROM mempool;")
        self.conn.commit()

    def get_current_diff(self) -> str:
        """Get the current difficulty and return it

        :return: _description_
        :rtype: str
        """
        self.cur.execute("SELECT hash, timestamp FROM blocks LIMIT 4")
        blocks = sorted(self.cur.fetchall(), key=lambda x: x[1])
        if blocks is not None:
            recent_block = blocks[-1]
            for idx, i in enumerate(recent_block[0]):
                if i != "0":
                    count = idx
                    break
            return count * "0"
        else:
            return "0000"

    def calculate_diff(self) -> str:
        """Calculate the new difficulty for blocks and change it according
           to the speed the blocks are mined

        :return: The difficulty
        :rtype: str
        """
        current_difficulty = self.get_current_diff()
        self.cur.execute("""SELECT hash, timestamp
                         FROM blocks
                         ORDER BY timestamp DESC
                        """)
        blocks = sorted(self.cur.fetchall(), key=lambda x: x[1])
        if len(blocks) % 4 == 0:
            block_deltas = []
            for idx, block in enumerate(blocks):
                if idx != 0:
                    block_deltas.append(block[1]-blocks[idx-1][1])
            if mean(block_deltas) > 60:
                return current_difficulty[:-1]
            elif mean(block_deltas) < 60:
                return current_difficulty + "0"
        else:
            return current_difficulty
