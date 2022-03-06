from node import Node
import time

n1 = Node("127.0.0.1", 4568, print, [])
n1.start()
n2 = Node("127.0.0.1", 4550, print, [])
n2.start()
nodes = []
for i in range(2):
    x = Node("127.0.0.1", 4569+i, print, [("127.0.0.1", 4568), ("127.0.0.1", 4550)])
    x.start()
    nodes.append(x)
    time.sleep(0.5)

while True:
    print(n1.client_tuples)
    print(n2.client_tuples)
    print("*"*50)
    for i in nodes:
        print(i.client_tuples)
        print(i.connect_list)
        print("*"*50)
    print("-"*50)
    time.sleep(1)



# import sys
# port = int(sys.argv[1])
# print(port)
# n1 = Node("127.0.0.1", port, print, [("127.0.0.1", 4568)])
# n1.start()
# while True:
#     print(n1.client_tuples)
#     time.sleep(1)