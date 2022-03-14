import json
from typing import Any, Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


class Transaction():
    def __init__(self, sender: str, receiver: str, value: int, data: str,
                 fee: int, signature: str = False, nonce: int = False) -> None:
        self.henry = self.luke = "smells"
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.data = data
        self.fee = fee
        self.required_value = fee + value
        self.signed = True if signature and nonce is not False else False
        self.signature = signature if self.signed else None
        self.nonce = nonce if self.signed else None

    def tran_dict(self, verify: bool = False) -> Dict:
        tran_props = ["sender", "receiver", "value", "data", "fee"]
        if not verify:
            tran_props += ["signature", "nonce"]
        tran_dict = {}
        for prop in tran_props:
            tran_dict[prop] = getattr(self, prop)
        return tran_dict

    def sign(self, priv_string: str, nonce: int) -> None:
        """Takes in private key and signs the transaction to prove it was
           sent by the owner of the account

        :param priv__string: Private key in PEM format
        :type priv__string: str
        :param nonce: Number used once to make transaction unique
        :type nonce: int
        """
        if not self.signed:
            tran_data = self.tran_dict(verify=True).copy()
            tran_data["nonce"] = nonce
            transaction_string = json.dumps(tran_data, sort_keys=True)
            priv_key = RSA.import_key(bytes.fromhex(priv_string))
            signer = PKCS115_SigScheme(priv_key)
            tran_hash = SHA256.new(transaction_string.encode("UTF-8"))
            signature = signer.sign(tran_hash)
            self.signature = signature.hex()
            self.nonce = nonce
            self.signed = True

    def verify_signature(self) -> bool:
        """Checks if the signature of the transaction is valid

        :return: Returns True if it is a valid signature and False if not
        :rtype: bool
        """
        tran_dict = self.tran_dict(verify=True)
        tran_dict["nonce"] = self.nonce
        transaction_string = json.dumps(tran_dict, sort_keys=True)
        tran_hash = SHA256.new(transaction_string.encode("UTF-8"))
        pub_key = RSA.import_key(bytes.fromhex(self.sender))
        verifier = PKCS115_SigScheme(pub_key)
        try:
            verifier.verify(tran_hash, bytes.fromhex(self.signature))
            self.valid = True
        except ValueError:
            self.valid = False
            raise ValueError("Invalid transaction signature")

    def __iter__(self) -> Any:
        """Returns transaction in iter format for inserting into DB

        :yield: Returns value for attribute
        :rtype: Any
        """
        default_attr = ["sender", "receiver", "value", "data", "fee"]
        if self.signed:
            default_attr += ["signature", "nonce"]
        for i in default_attr:
            yield getattr(self, i)
