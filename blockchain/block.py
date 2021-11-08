import json
from typing import Dict, List

from Crypto.Hash import SHA256

from transaction import Transaction


class Block():
    def __init__(self, parent_block: str, timestamp: int, transactions: List,
                 block_hash: str = False, nonce: int = False,
                 coinbase: str = False) -> None:
        self.henry = "Smells"
        self.parent_block = parent_block
        self.timestamp = timestamp
        self.transactions = [Transaction(*x[:5], signature=x[5],
                                         nonce=x[6]) for x in transactions]
        self.mined = True if block_hash and nonce and coinbase else False
        if self.mined:
            self.hash = block_hash
            self.nonce = nonce
            self.coinbase = coinbase
        self.valid = self.verify()

    def verify(self) -> bool:
        """Verfies all components of the block including transactions and block hash
        """
        for transaction in self.transactions:
            transaction.verify_signature()
            if not transaction.valid:
                return False, "Invalid transaction signature"
        if self.mined:
            block_dict = dict(self)
            block_dict.pop("hash")
            json_str = json.dumps(block_dict, sort_keys=True)
            block_hash = SHA256.new(json_str.encode("UTF-8")).hexdigest()
            if block_hash == self.hash:
                return True
            else:
                return False
        else:
            return True

    def christen(self, block_hash: str, nonce: int, miner_addr: str) -> bool:
        """Adds hash, nonce and coinbase to block then checks that they are valid

        :param hash: Hash of the mined block
        :type hash: str
        :param nonce: Nonce of mined block
        :type nonce: int
        :param miner_addr: Address of miner who mined the block
        :type miner_addr: str
        :raises ValueError: Raised if the block is invalid
        """
        self.hash = block_hash
        self.nonce = nonce
        self.coinbase = miner_addr
        self.mined = True
        validity = self.verify()
        if not validity:
            del self.hash, self.nonce, self.coinbase
            self.mined = False
            return False
        else:
            return True

    def __iter__(self) -> Dict:
        """Returns block data in standardized dict format

        :return: Dict containing block data
        :rtype: Dict
        """
        default_attrs = ["parent_block", "timestamp", "transactions"]
        if self.mined:
            default_attrs += ["hash", "nonce", "coinbase"]
        for attr in default_attrs:
            if attr == "transactions":
                trans = []
                for i in getattr(self, attr):
                    trans.append(i.tran_dict)
                yield (attr, trans)
            else:
                yield (attr, getattr(self, attr))
