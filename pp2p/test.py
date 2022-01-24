from node import Node
import time

n1 = Node("127.0.0.1", 4568, print, [])
n1.start()

n2 = Node("127.0.0.1", 4569, print, [("127.0.0.1", 4568)])
n2.start()

n3 = Node("127.0.0.1", 4570, print, [("127.0.0.1", 4569)])
n3.start()


while True:
    print(f"Node 1 {n1.client_tuples}")
    print(f"Node 1 {n1.connect_list}, {n1.id}")
    print(f"Node 2 {n2.client_tuples}, {n2.id}")
    print(f"Node 2 {n2.connect_list}, {n2.id}")
    print(f"Node 3 {n3.client_tuples}, {n3.id}")
    print(f"Node 3 {n3.connect_list}, {n3.id}")
    print("-"*50)
    time.sleep(1)
    n1.send_all({"hello": "world"})
