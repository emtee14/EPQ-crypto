from block import Block
from miner import Miner
from transaction import Transaction
from Crypto.PublicKey import RSA

if __name__ == "__main__":
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

    transaction = tuple(new_tran)
    genesis = Block("", 1635806900, [transaction])
    block_miner = Miner(dict(genesis), "1", "jhfbwhfq", workers=4)
    block_miner.mine_block()
    validity = genesis.christen(block_miner.hash, block_miner.nonce,
                                block_miner.miner_addr)
    if validity:
        print("✅ - Test passed block.py")
    else:
        print("❌ - Test failed block.py")
