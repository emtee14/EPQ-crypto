import json
import sqlite3
from typing import Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

"""
DB schema
Block db - all blocks along with their data except transactions (block_number, hash, nonce, prev_block_hash, timestamp)
Transation DB - contains all transactions along with the block they are asociated with (block_hash, sender, reciever, amount, signature, timestamp)
"""

class Transaction():
    def __init__(self, transcation_dict, signed=False) -> None:
        self._tran_dict = transcation_dict
        self.signed = signed
        self.import_tran()
        self.valid = False
        if signed:
            self.signature = transcation_dict["signature"]
            self._tran_dict.pop("signature")
            self.verify_signature()

    def sign(self, priv_key: str) -> None:
        """Takes in private key and signs the transaction to prove it was sent by the owner
           of the account

        :param priv_key: Private key in PEM format
        :type priv_key: str
        """
        if not self.signed:
            transaction_string = json.dumps(self._tran_dict)
            priv_key = RSA.import_key(priv_key)
            signer = PKCS115_SigScheme(priv_key)
            tran_hash = SHA256.new(transaction_string.encode("UTF-8"))
            signature = signer.sign(tran_hash)
            self.signature = signature.hex()
            self.signed = True

    def verify_signature(self) -> bool:
        """Checks if the signature of the transaction is valid

        :return: Returns True if it is a valid signature and False if not
        :rtype: bool
        """
        transaction_string = json.dumps(self._tran_dict)
        tran_hash = SHA256.new(transaction_string.encode("UTF-8"))
        pub_key = RSA.import_key(self._tran_dict["sender"])
        verifier = PKCS115_SigScheme(pub_key)
        try:
            verifier.verify(tran_hash, bytes.fromhex(self.signature))
            self.valid = True
        except ValueError:
            self.valid = False

    @property
    def tran_dict(self) -> Dict:
        """Returns a dict containing all the transaction infomation

        :return: Dict containing all transaction info
        :rtype: Dict
        """
        tran_dict = self._tran_dict.copy()
        if self.signed:
            tran_dict["signature"] = self.signature
        return tran_dict

    def import_tran(self) -> None:
        """Creates parameters for all info in the transaction
        """
        self.sender = self._tran_dict["sender"]
        self.reciever = self._tran_dict["reciever"]
        self.amount = self._tran_dict["amount"]
        self.timestamp = self._tran_dict["timestamp"]
        if self.signed:
            self.signature = self._tran_dict["signature"]


class Block():
    def __init__(self, block_dict, mined: bool = True) -> None:
        self.henry = "Smells"
        self.block_dict = block_dict
        self.mined = mined
        self.valid = False
        self.import_block()

    def import_block(self):
        self.number = self.block_dict["block_number"]
        if self.mined:
            self.hash = self.block_dict["hash"]
            self.nonce = self.block_dict["nonce"]
        self.prev_block = self.block_dict["prev_block_hash"]
        self.timestamp = self.block_dict["timestamp"]
        self.transactions = []
        for transaction in self.block_dict["transactions"]:
            tran_obj = Transaction(transaction, signed=True)
            tran_obj.verify_signature()
            if tran_obj.valid:
                self.transactions.append(tran_obj)
            else:
                print("Fatal error somewhere invalid transaction saved to blockchain")

    def mine_block(self):
        nonce = 0
        while self.mined == False:
            temp_block = self.block_dict.copy()
            temp_block["nonce"] = nonce
            block_string = json.dumps(temp_block)
            block_hash = SHA256.new(block_string.encode("UTF-8")).hexdigest()
            if block_hash[:5] == "14605":
                self.mined = True
                self.hash = block_hash
                self.nonce = nonce
                self.block_dict["hash"] = block_hash
            nonce +=1
            

    def verify_block(self):
        block_no_hash = self.block_dict.copy()
        block_no_hash.pop("hash")
        block_no_hash["nonce"] = self.nonce
        block_string = json.dumps(block_no_hash)
        block_hash = SHA256.new(block_string.encode("UTF-8")).hexdigest()
        if block_hash == self.hash:
            self.valid = True
        else:
            self.valid = False


