import sqlite3
from typing import Dict

from Crypto.PublicKey import RSA

from block import Block


class Blockchain():
    def __init__(self, db="blockchain.db") -> None:
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.verify_db()

    def verify_db(self) -> None:
        """If tables do not exist in DB they will be created
        """
        self.cur.execute("""SELECT name FROM sqlite_master WHERE type='table'
                            AND name='transactions' OR name='blocks';""")
        if not (len(self.cur.fetchall()) == 2):
            self.cur.execute("""CREATE TABLE blocks (block_number INT,hash
                                VARCHAR(64),nonce INT,parent_block VARCHAR(64),
                                timestamp INT);""")
            self.cur.execute("""CREATE TABLE transactions (parent_block VARCHAR(64),
                                sender VARCHAR(2000),receiver VARCHAR(2000),
                                amount INT,signature VARCHAR(512));""")
            self.conn.commit()

    def get_block(self, block_number: int = None,
                  block_hash: str = None) -> Block:
        """Returns a Block object of the desired block containing all it's data

        :param block_number: The number for the requested
                             block, defaults to None
        :type block_number: int, optional
        :param block_hash: The hash for the requested block, defaults to None
        :type block_hash: str, optional
        :return: Block object containing all block data
        :rtype: Block
        """
        if block_number is None and block_hash is None:
            return
        if block_number:
            self.cur.execute("SELECT * FROM blocks WHERE block_number = ?",
                             (block_number,))
        else:
            self.cur.execute("SELECT * FROM blocks WHERE hash = ?",
                             (block_hash,))
        block_tuple = self.cur.fetchone()
        self.cur.execute("SELECT * FROM transactions WHERE block_hash = ?",
                         (block_tuple[1]))
        transaction_list = self.cur.fetchall()
        block = {
            "block_number": block_tuple[0],
            "hash": block_tuple[1],
            "nonce": block_tuple[2],
            "prev_hash": block_tuple[3],
            "timestamp": block_tuple[4],
            "transactions": []
        }
        for transaction in transaction_list:
            block["transactions"].append({
                "sender": transaction[1],
                "receiver": transaction[2],
                "amount": transaction[3],
                "signature": transaction[4],
            })
        return Block(block)

    def account_info(self, public_key: str,
                     return_transactions: bool = False) -> Dict:
        """Returns account balance and transaction history on given account

        :param public_key: Public key to identify account
        :type public_key: str
        :param return_transactions: Whether or not to return transaction
                history along with balance, defaults to False
        :type return_transactions: bool, optional
        :return: Current balance and transaction history is specified
        :rtype: Dict
        """
        public_key = RSA.import_key(public_key)
        key_str = public_key.export_key().decode("UTF-8")
        balance = 0
        self.cur.execute("""SELECT * FROM transactions WHERE
                            sender = ? OR receiver = ?""",
                         (key_str, key_str,))
        transactions = self.cur.fetchall()
        for transaction in transactions:
            if transaction[1] == key_str:
                balance += -(transaction[3])
            elif transaction[2] == key_str:
                balance += transaction[3]
        if return_transactions:
            tran_history = []
            for i in transactions:
                self.cur.execute("SELECT timestamp FROM blocks WHERE hash = ?",
                                 (i[0],))
                tran_history.append({
                    "parent_block": i[0],
                    "sender": i[1],
                    "receiver": i[2],
                    "amount": i[3],
                    "signature": i[4],
                    "timestamp": self.cur.fetchone()[0]
                })
            return {"balance": balance, "transaction_history": tran_history}
        return {"balance": balance}

    def add_block(self, block: Block) -> None:
        """Validates block and all transactions contained within then adds it
           to blockchain

        :param block: Block object for the block you wish to be added
        :type block: Block
        :raises ValueError: Raises error if there is an error in the validity
                of the block
        """
        block.verify_block()
        if block.valid:
            self.cur.execute("""SELECT MAX(block_number) as max_number
                             FROM blocks;""")
            parent_block_num = self.cur.fetchone()
            genesis = False
            if parent_block_num is None and block.number == 1:
                parent_block_num = [""]
                genesis = True
            if block.number-1 == parent_block_num[0] or genesis:
                for tran in block.transactions:
                    sender_bal = self.account_info(tran.sender)
                    if not (sender_bal["balance"] >= tran.amount):
                        raise ValueError("Account doesn't have enough funds")
                block_tuple = (block.number, block.hash, block.nonce,
                               block.prev_block, block.timestamp)
                self.cur.execute("""INSERT INTO blocks (block_number, hash, nonce, parent_block, timestamp)
                                 VALUES (?, ?, ?, ?, ?);""", block_tuple)
                self.conn.commit()
                for tran in block.transactions:
                    tran_tuple = (block.hash, tran.sender, tran.receiver,
                                  int(tran.amount), tran.signature)
                    self.cur.execute("""INSERT INTO transactions (parent_block, sender, receiver, amount, signature)
                                     VALUES (?, ?, ?, ?, ?);""", tran_tuple)
                    self.conn.commit()

    @property
    def prev_hash(self) -> str:
        """Returns the hash of the most recent block

        :return: SHA256 hash of most recent block
        :rtype: str
        """
        self.cur.execute("SELECT MAX(block_number) as max_number FROM blocks;")
        prev_block = self.cur.fetchone()[0]
        self.cur.execute("SELECT hash FROM blocks WHERE block_number = ?",
                         (prev_block,))
        return self.cur.fetchone()[0]

    @property
    def prev_number(self) -> int:
        """Returns the number of most recent block

        :return: Number for most recent block
        :rtype: int
        """
        self.cur.execute("SELECT MAX(block_number) as max_number FROM blocks;")
        prev_block = self.cur.fetchone()[0]
        return prev_block
