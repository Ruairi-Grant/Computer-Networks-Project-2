import socket
import time
import sys

eta = 120

if len(sys.argv) < 4:
    print(f"Usage: {sys.argv[0]} <start_node> <node_list[0]> <node_list[1]> ...")
    sys.exit(1)

node_id = sys.argv[1]
print(f"RSU {node_id} client process active.")

print(f"Node list read in: {sys.argv[1]}, {sys.argv[2]}, {sys.argv[3]}")

# need to know hostname of node.py using hostname -I
# need different port numbers for each
if sys.argv[2] == "A":
    host = "10.35.70.4"
    port = 33500    
if sys.argv[2] == "B":
    host = "10.35.70.4"
    port = 33501
if sys.argv[2] == "C":
    host = "10.35.70.4"
    port = 33502    
if sys.argv[2] == "D":
    host = "10.35.70.4"
    port = 33503  
if sys.argv[2] == "E":
    host = "10.35.70.4"
    port = 33504

serverAddressPort = (host, port)
buffer = 1024
i = 0
finished = False

# Path planning algorithm will be implemented here to generate a list of nodes along the Bus's route
def generate_node_list():
    return ("A B C /")

# Bus acquires the address and port of the next RSU in its node list from a database
def node_ip_address(node):
    return ("127.0.0.1", 65432)

# ETA calculating algorithm will be implemented here
def return_eta():
    return(120)

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Generate the node list that the EV needs to contact
node_list = generate_node_list()

# Search for the IP address of the node we want to contact
# serverAddressPort = node_ip_address(node_list[0])

# Send to server using created UDP socket
while not finished:

    eta = return_eta()
    eta = eta - i # this is simply to simulate the ETA reducing over time as the EV gets closer
    converted_eta = str(eta)

    msgFromClient = node_list + converted_eta
    bytesToSend = str.encode(msgFromClient)
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    
    time.sleep(3)
    i = i + 10 
    if eta < 10: # if the EV is within 10 seconds of the light, stop sending telemetry
        finished = True

print("Finishing connection")
msgFromServer = UDPClientSocket.recvfrom(buffer)

msg = "Message from RSU {}".format(msgFromServer[0])

print(msg)