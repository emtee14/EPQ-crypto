from main import cryptoNode;server_node = cryptoNode(port=3467, bootstrap=[("127.0.0.1", 14065)],api=False);server_node.start()
