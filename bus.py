import socket
import time

eta = 120

serverAddressPort = ("127.0.0.1", 65432)
buffer = 1024
i = 0
finished = False

# Path planning algorithm will be implemented here to generate a list of nodes along the EV's route
def generate_node_list():
    return ("A B C /")

# EV acquires the address and port of the next RSU in its node list from a database
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
serverAddressPort = node_ip_address(node_list[0])

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