import json
import sqlite3
from typing import Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme

"""
DB schema
Block db - all blocks along with their data except transactions (block_number, hash, nonce, prev_block, timestamp)
Transation DB - contains all transactions along with the block they are asociated with (block_hash, sender, reciever, amount, signature, timestamp)
"""

class Transaction():
    def __init__(self, transcation_dict, signed=False) -> None:
        self._tran_dict = transcation_dict
        self.signed = signed
        self.import_tran()

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
        return self.valid

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
