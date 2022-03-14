

if __name__ == "__main__":
    from blockchain.block import Block
    from blockchain.miner import Miner
    from blockchain.transaction import Transaction
    from blockchain.blockchain import Blockchain
    from Crypto.PublicKey import RSA

    blockchain = Blockchain(lambda x, y, z: print(x, y, z))
    with open('./testing/priv-key1.pem', 'r') as f:
        sender = RSA.import_key(f.read())
    with open('./testing/priv-key2.pem', 'r') as f:
        receiver = RSA.import_key(f.read())

    genesis = Block("", 111, [])
    block_miner = Miner(dict(genesis), "f",
                        sender.public_key().exportKey("DER").hex(), workers=4)
    block_miner.mine_block()
    validity = genesis.christen(block_miner.hash, block_miner.nonce,
                                block_miner.miner_addr)
    blockchain.add_block(genesis)

    tran_obj = Transaction(sender.public_key().exportKey("DER").hex(),
                           receiver.public_key().exportKey("DER").hex(), 5, "",
                           5*0.05)
    tran_obj.sign(sender.export_key("DER").hex(),
                  blockchain.get_tran_nonce(sender.public_key().exportKey("DER").hex()))
    print(tran_obj.verify_signature())
    transaction = tuple(tran_obj)

    new_block = Block(blockchain.prev_hash, 112, [transaction])
    print(dict(new_block))
    block_miner = Miner(dict(new_block), "f",
                        sender.public_key().exportKey("DER").hex())
    block_miner.mine_block()
    new_block.christen(block_miner.hash, block_miner.nonce,
                       block_miner.miner_addr)
    blockchain.add_block(new_block)

    print(blockchain.get_balance(sender.public_key().exportKey("DER").hex()))
    print(blockchain.get_balance(receiver.public_key().exportKey("DER").hex()))
    print(blockchain.get_block(genesis.hash))
