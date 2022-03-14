from flask import Flask, g
from web_api import routes
import time


def create_app(blockchain, node, log):
    app = Flask(__name__)

    app.register_blueprint(routes.bp, url_prefix="/api")

    @app.before_request
    def before_request_func():
        g.node = node
        g.blockchain = blockchain
        g.log = log

    return app
