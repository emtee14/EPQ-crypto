import json
from typing import Dict

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


class Transaction():
    def __init__(self, sender: str, receiver: str, value: int, data: str,
                 fee: int, signature: str = None, nonce: int = None) -> None:
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.data = data
        self.fee = fee
        self.signed = True if signature and nonce else False
        self.signature = signature if self.signed else None
        self.nonce = nonce if self.signed else None

    @property
    def tran_dict(self) -> Dict:
        tran_props = ["sender", "receiver", "value", "data", "fee"]
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
            tran_data = self.tran_dict.copy()
            tran_data["nonce"] = nonce
            transaction_string = json.dumps(tran_data)
            priv_key = RSA.import_key(priv_string)
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
        tran_dict = self.tran_dict.copy()
        tran_dict["nonce"] = self.nonce
        transaction_string = json.dumps(tran_dict)
        tran_hash = SHA256.new(transaction_string.encode("UTF-8"))
        pub_key = RSA.import_key(self.sender)
        verifier = PKCS115_SigScheme(pub_key)
        try:
            verifier.verify(tran_hash, bytes.fromhex(self.signature))
            self.valid = True
        except ValueError:
            self.valid = False
            raise ValueError("Invalid transaction signature")


def test():
    sender = RSA.import_key("""-----BEGIN RSA PRIVATE KEY-----\n
                            MIIEpAIBAAKCAQEAodIjKtTvrbDp5YJKxuVig1BbKwwddUwWUQz/GTdYysAUK+8l\n
                            G2uI9JEzy9dn9Rn6TeHYvZJGaTFRjjwdl8unq4p+QRTYM545I9C+1jSNQmonyzqJ\n
                            TdlzCl7XLHPM3EVJ+1gxak6q5iwE+A7bp6Wp5ojC1AJ49DxN4N+gvxTyWkGkBE1u\n
                            yGkwOfIHz1AKQR+P8neVtl2PqtaANzrb4iaDlf3AMDtEI4qdwQuBCeJNh4cxWeIm\n
                            Cyd1orCqTLyjs4hO0+EgmFJqI5sQ9N6Ah4fZ02Rqb1uDrbLdZVaprbrbIQZxZBpQ\n
                            JQaYPL6vluxOzncvFF251ghl6uTompy4v6nHIwIDAQABAoIBAC/XoO4Y5oPDumNQ\n
                            kisbxnRsXYfsnQkA5dgwr3sVEftfrpcOrTneIS+tflLV7LZaZ9Z+30Ws6YRQQHx8\n
                            6YLngzsERy+WqhUYwmwEW2eZQepQ2FMNi2qoz4pRX+yUkAzPr3/QI0v61iwW96Ef\n
                            Q3HdWM3/wRpNYNVUvvGtLClSWBS2um7SvHaGzMvezHZ744w52Gw5JxKznNeoc+Qs\n
                            sS20Z+jGUmR39YBQTSYD5GwrRZy/CLaWO3rLsNnKM9Yzbf0hxe8h2/SqwIByKNMg\n
                            D4bQ/EddIz6htcG3DA2rPrb+cbyNtQq7p5HpJHKijfXYqdaZzJKKISHrPT5BCa/N\n
                            6ZyZm4ECgYEAtv6Lh0AQHn5ebtJ8YUkZI9uE9adlhr5HKtvoqBDJy5YAv6AMkkWC\n
                            UBE8QNKj2IWFJucZ01wds0lwj0DYl83BSUPmMJpEAHa9V9NZ7tqDjxIyG60CKdy6\n
                            MbTTZIsVwgLpzC31b6PkYmosviEUnFauFoohA6dW66mX1pLRr1S14k0CgYEA4mEe\n
                            IpnZw+dkxONZV0NQ+8IoRrFkEGKo+JlAlfq40CLkVTC0zJrxgZtKW0YLstc+o6LI\n
                            gc+1rmewz5KqR7cP6aVwic1YwXfFSkozJY/WYNdExTJSvVadlrLz/d2OXQqrvTL2\n
                            wycR2Ul+Roqu5udatJkoXoFlmP5PtrJJ9gq5py8CgYEAtQgIfJqx15joTvZIOe4Y\n
                            wtJuLJ+X3r7qpMm81lcVayRQRUJObX36Nr92PiKkGJWubhf+AoyEjVM/2VgrbbIN\n
                            Xy+ez8ItN9A/7FyYAaWGtMkpbRuwoj1MrdPXtQWrVq2PIYDt563ZSEsFTGppe2h8\n
                            /KtVkcnAQY8bORkx+yPwc5kCgYBwetbRVGZaK3frSBdU/3KWlOMUNQHGDm9sjiEE\n
                            JD591Ehld7ztyLLktfcdINGhO8e44KIFteHM1WKJ0JLg7Tlv2y7umWRXRJ53iiSd\n
                            rjlThsJ5xMZNo2LLxQDsi5A39JxedpsbXidFMnoWrMO4oQ11nH/tbRfBC+MpoK6V\n
                            HMEgKwKBgQCHwM+vuxE6VqE1Te5InlgTe5hMuzvrOgQt2QkCyX4iFuM5RsnfyTJl\n
                            gEJqtvtOjwbbWut3q6Qvro0GN/5MnQBR3jKqKsdIluvY9xpe0zGvfUC/+GGjygti\n
                            a2nlqKHz5KXOq5V6Gji9xNOXq1xX7P976r5Mmm4FuUdk+6+JFfq3dw==\n
                            -----END RSA PRIVATE KEY-----""")
    receiver = RSA.import_key("""-----BEGIN RSA PRIVATE KEY-----\n
                              MIIEowIBAAKCAQEAjy5k/XyifOxkzaaFQkMrWen7XCQKTfTcXcbPgpA4oeu9TTN1\n
                              NbybSGLSd5cBUYBWQzJ//NUJnv8eaJQXrnFoC+uw9Ol192jp5x2PjoqduCjpKEgu\n
                              dYU4g7FGtDL1PowcpuKJNxbk4+0sLiwbh28iTrlt+i6nTEiMtuP6l+PRDqxCTd4J\n
                              8YbexWYCpfdjtxIaKP38VGaZgVUMxyQxrq9Uau30aoCPZMyfrhPLk7GyIipW8PR5\n
                              cy3Wx6CD7QBwA4AbBakvnRao6Elb2B5pzs/5NtmMn2ERKUy+kMPFX2K2xIsTG1ks\n
                              yH30MdiAAPtYGcMKyEcdsoJsATqusVqi8JsX5QIDAQABAoIBAAFE2ylHTatcxFHx\n
                              nAm9Iv5jgqeg5s8lEJTrhP2hE0IVdEfhtl65DV6ZXZ3TYp7Fy+iW4yfVqDBWuNQa\n
                              x+ZIZAXYW2j4RA7iyPvpjlL9ldiYKDouquwTYlpXG7YkziP1RZsRs+n0k9Jp+4kX\n
                              OVE8d2nfiS19SgdKN1EMTorCaUu/e1uW4kwVITKPiohr/UjVLq+mK+KPp9wDI6ds\n
                              /h6tsKcmOPgxcqqqHCFljc3vONk8F23p6DQ5UMFzndMPdSYxrNUuwzig2KJzByPM\n
                              VhC9P20ISmgsjBeuz1R/gLEmJKveztkEp6W3DqQxu9CfJbFSi2my28e8gJ3y2uH9\n
                              WO6uWrECgYEAuH7DFy53NJyVVAfqlSC3REt2PfkO70Oi/70bGW9kR13R5zS4vf67\n
                              OapWEJW/NMD/PS66V5hnXqJHbtz4RtuHjXnp4YwW0yDxlboVRc6+/eYfk8xD4R12\n
                              ix0TOFu6k/4A+Mj9R+upOH6TzPqOccIyrGNdD4wPvtc4WuRtjTfwXg0CgYEAxqyM\n
                              DLUQIQDlWxzBM5i4VrX/1PPlZl2To77lqwOCSsDEu0S6lXss43o4dojYETII8aYE\n
                              mmoVJsizYxH24RnMLDQkyth7Df2OdeedN8zy3V44fip5s0mCv1OWwcN0NPyv1mBj\n
                              Yx7HgCmET0KHyy0TBQkxZFkCWc+rIkj32BPsAzkCgYBQr++2lbXAprKQO54WdmZw\n
                              Ueh2lhQ4BAanfhb5+sOKiregPGiHf352a86UFkm3UqjOIz+Py7F5q9M94xoaMyyH\n
                              bUgiQlhBIelGKEnha9gPxrMMuor9SxtrH94mCcgBrVbTd2N+LsylToZpYTMnAV2U\n
                              EyjCAelo90tIRRq8ZjiTiQKBgEuDnh/eWmkQ/Bxri4vfCoH632jD43fLLajZkFY2\n
                              GTnsl1pOv1S94sv70qZLUUUH7Zpb7ff7RlrdgkGvvFTHB3Htx+ZJ7kvdCl8KUBm7\n
                              jrxRacuavXNGB6pNTUoMzoitWvBy5pPwSQgPv7iYoyC42zfYzKtFob0dUADSF1JM\n
                              EDMRAoGBAIwqCR8WUT5dAoh0r1lRRblyjLyYMHtyycfSGhTxnb1Ufkj0rt1/3Xkq\n
                              p/azoYLf06S7IHwt2OyhWDdNMlDj/ekSiHOsQqSarFtAPpSAz3KKgyoQLnrp6GPR\n
                              7sirJt00odZBRi/pKxLf8dulD9q0X3k9B/IaTgP6n0Dyc4/q+4N4\n
                              -----END RSA PRIVATE KEY-----""")
    new_tran = Transaction(sender.public_key().exportKey().decode("UTF-8"),
                           receiver.public_key().exportKey().decode("UTF-8"),
                           20, "", 20*0.005)
    new_tran.sign(sender.export_key().decode("UTF-8"), 0)
    new_tran.verify_signature()
    if new_tran.valid:
        print("✅ - Test passed transaction.py")
    else:
        print("❌ - Test failed transaction.py")
