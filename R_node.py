

from socket import *
from threading import *

# Temporary for testing
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432 #33500  # The port used by the server

def SendToServer(nodeList):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(nodeList)
        data = s.recv(1024)

    print(f"Received {data!r}")

def Receiving(sock):
    while True:
        # decode data and use c.py to send it
        data, addr = sock.recvfrom(1024)
        data = data.decode('ascii')
        nodes, eta = data.split('/')
        nodes = nodes.strip()
        nodes = nodes.split(' ')
        print("Travel Route: ", nodes, "\nETA to first node: ", eta)
        print("Start clearing traffic between ", nodes[0], " and ", nodes[1])
        if len(nodes)>2:
            SendToServer(data[1:].encode('ascii'))


my_addr =('127.0.0.1',65432)
#t_ip = '127.0.0.1' 
#target =(t_ip, 65432)
#node_table = {'C':(t_ip, 65432)}


s = socket(AF_INET, SOCK_DGRAM)
s.bind(my_addr)

print("waiting connection")



x = Thread(target=Receiving, args=(s,))
x.start()

#wel="OK!"
#for key in node_table:
    #target = node_table[key]
    #s.sendto(wel.encode('ascii'), target)
