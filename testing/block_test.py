from blockchain.block import Block
from blockchain.miner import Miner
from blockchain.transaction import Transaction
from Crypto.PublicKey import RSA


def test():
    with open('./testing/priv-key1.pem', 'r') as f:
        sender = RSA.import_key(f.read())
    with open('./testing/priv-key1.pem', 'r') as f:
        receiver = RSA.import_key(f.read())
    tran_obj = Transaction(sender.public_key().exportKey().decode("UTF-8"),
                           receiver.public_key().exportKey().decode("UTF-8"),
                           20, "", 20*0.005)
    tran_obj.sign(sender.export_key().decode("UTF-8"), 0)
    transaction = tuple(tran_obj)

    genesis = Block("", 1635806900, [transaction])
    block_miner = Miner(dict(genesis), "1", "jhfbwhfq", workers=4)
    block_miner.mine_block()
    validity = genesis.christen(block_miner.hash, block_miner.nonce,
                                block_miner.miner_addr)
    if validity:
        print("✅ - Test passed block.py")
    else:
        print("❌ - Test failed block.py")
