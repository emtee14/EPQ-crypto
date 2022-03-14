from blockchain.blockchain import Blockchain
from blockchain.transaction import Transaction
from Crypto.PublicKey import RSA
from flask import Blueprint, g, jsonify, request

bp = Blueprint("routes", __name__)


@bp.route("/get_bal", methods=["GET"])
def get_bal():
    blockchain = Blockchain(g.log, db=g.blockchain)
    account = request.args.get("address", None)
    if account is None:
        return {"msg": "Invalid address", "error": True}, 404

    try:
        bal = blockchain.get_balance(account)
    except Exception as e:
        return {"msg": str(e), "error": True}, 500

    return jsonify(account=account, balance=bal), 200


@bp.route("/get_block", methods=["GET"])
def get_block():
    blockchain = Blockchain(g.log, db=g.blockchain)
    block_hash = request.args.get("hash", None)
    if block_hash is None:
        return {"msg": "Invalid hash", "error": True}, 404
    try:
        block = blockchain.get_block(block_hash)
    except Exception as e:
        return {"msg": str(e), "error": True}, 500
    return dict(block), 200


@bp.route("/get_recent_block", methods=["GET"])
def get_recent_block():
    blockchain = Blockchain(g.log, db=g.blockchain)
    block_hash = blockchain.prev_hash
    block = blockchain.get_block(block_hash)
    return dict(block)


@bp.route("/get_history", methods=["GET"])
def get_history():
    blockchain = Blockchain(g.log, db=g.blockchain)
    account = request.args.get("address", None)
    if account is None:
        return {"msg": "Invalid address", "error": True}, 404
    try:
        history = blockchain.get_transactions(account)
    except Exception as e:
        return {"msg": str(e), "error": True}, 500
    return history, 200


@bp.route("/add_transaction", methods=["POST"])
def add_transaction():
    private_key = request.json.get("priv_key", None)
    amount = request.json.get("amount", None)
    data = request.json.get("data", "")
    receiver = request.json.get("receiver", None)
    if None in [private_key, amount, receiver]:
        return {"msg": "Missing attribute", "error": True}, 404

    blockchain = Blockchain(g.log, db=g.blockchain)

    priv_key_obj = RSA.import_key(bytes.fromhex(private_key))
    public_key = priv_key_obj.public_key().export_key("DER").hex()

    transaction = Transaction(public_key, receiver, amount, data, amount*0.005)
    nonce = blockchain.get_tran_nonce(public_key)
    transaction.sign(private_key, nonce)
    transaction.verify_signature()
    if transaction.valid:

        signed_tran = {}
        keys = ["sender", "receiver", "value",
                "data", "fee", "signature", "nonce"]
        for idx, i in enumerate(transaction):
            signed_tran[keys[idx]] = i

        blockchain.add_to_mempool(signed_tran)
        msg = {
            "type": "add_transaction",
            "data": signed_tran,
            "node_id": g.node.id
        }
        g.node.send_all(msg)
        return signed_tran, 200
    else:
        return {"msg": "Unable to verify signature", "error": True}, 500
