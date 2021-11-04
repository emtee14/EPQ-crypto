from Crypto.PublicKey import RSA
from blockchain.transaction import Transaction


def test():
    with open('./testing/priv-key1.pem', 'r') as f:
        sender = RSA.import_key(f.read())
    with open('./testing/priv-key1.pem', 'r') as f:
        receiver = RSA.import_key(f.read())
    new_tran = Transaction(sender.public_key().exportKey().decode("UTF-8"),
                           receiver.public_key().exportKey().decode("UTF-8"),
                           20, "", 20*0.005)
    new_tran.sign(sender.export_key().decode("UTF-8"), 0)
    new_tran.verify_signature()
    if new_tran.valid:
        print("✅ - Test passed transaction.py")
    else:
        print("❌ - Test failed transaction.py")
