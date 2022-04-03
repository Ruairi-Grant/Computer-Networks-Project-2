# possibly don't need selector for client connections? as we are only establishing one connection each time the client is run...

import sys # among other things, because we are reading arguments from the console upon startup
import socket # for socket programming
import selectors # to enable multiple connections asynchronously 
import types # so that SimpleNamespace can be used

selector = selectors.DefaultSelector()
messages = [b"RSU client process online.", "", ""] # two extra message slots to store the (length-2) node list

# parameters: host = the host name (IP address) of the RSU to contact 
#             port = the server port number we want to write to
def connect_to_server(host, port):
    server_address = (host, port) # store the server IP address and port number to a server_addr object
    print(f"Starting connection to {server_address}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket for a TCP connection
    client_socket.setblocking(False) # set this socket to non-blocking mode
    client_socket.connect_ex(server_address) # connect this new socket to the server socket 

    events = selectors.EVENT_READ | selectors.EVENT_WRITE # client needs to know when the server is ready for both reading and writing and thus a bitwise OR operation is necessary
    
    # the data needed to track interactions with the server socket are stored to a data object using SimpleNamespace
    data = types.SimpleNamespace( 
        server_id = server_address, # for printing to the console
        sent_total = sum(len(m) for m in messages), # tracks the total number of bytes sent to the server
        received_total = 0, # tracks the amount of bytes echoed back - used to detect when a full confirmatory echo is received from the server
        messages = messages.copy(), # to track if there are still unsent messages
        outb=b"", # buffer for sending data to the server
        ) 

    # once the new client socket has been created, connected to the server, and had its data object created, register it with the selector
    selector.register(client_socket, events, data=data)


def service_connection(key, mask):
    server_socket = key.fileobj # sock now represents the server socket object
    data = key.data # data now represents the data object associated with the socket object

    if mask & selectors.EVENT_READ: # if the mask and selectors.EVENT_READ both evaluate to true, then the server socket is ready for READING (from)
        recv_data = server_socket.recv(1024)  # read data in from the server

        if recv_data: # if data is successfully read in
            print(f"Received {recv_data!r} from {data.server_id}") 
            data.received_total += len(recv_data) # increment the count of the data read in from the server
        
        if not recv_data or data.received_total == data.sent_total :  # if no data is received or a full confirmatory echo back is received
            print(f"Closing connection with {data.server_id}")
            selector.unregister(server_socket) # unregister the server socket from the selector
            server_socket.close() # close the connection to the server socket

    if mask & selectors.EVENT_WRITE: # if both true then the server socket is ready for WRITING to
        if not data.outb and data.messages: # if there is nothing in the send out buffer but there are messages still in the message object
            data.outb = data.messages.pop(0) # move the next item in the messages list to the data.outb buffer and then remove it from the list 
        if data.outb: # if there is a message to send out
            print(f"Sending {data.outb!r} to {data.server_id}")
            sent = server_socket.send(data.outb)  # send the message, then record the number of bytes sent
            data.outb = data.outb[sent:] # discard these bytes from the data out buffer 


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <start_node> <node_list[0]> <node_list[1]>")
    sys.exit(1)

node_id = sys.argv[1]
print(f"RSU {node_id} client process active.")

print(f"Node list read in: {sys.argv[2]}, {sys.argv[3]}")

if sys.argv[2] == "A":
    host = "127.0.0.1"
    port = 33500    
if sys.argv[2] == "B":
    host = "127.0.0.2"
    port = 33500
if sys.argv[2] == "C":
    host = "127.0.0.3"
    port = "33500"    
if sys.argv[2] == "D":
    host = "127.0.0.4"
    port = "33500"  
if sys.argv[2] == "E":
    host = "127.0.0.5"
    port = "33500"

messages[1] = str.encode(sys.argv[2])
messages[2] = str.encode(sys.argv[3])

connect_to_server(host, int(port))

try:
    while True:
        events = selector.select(timeout=1)
        if events: # if a server event has occurred (i.e. if connected to the server)
            for key, mask in events:
                service_connection(key, mask) # service the server connection

        # Check for a socket being monitored to continue.
        if not selector.get_map(): # if there is no connection to a server, break
            break

except KeyboardInterrupt:
    print("Client process terminated.")
finally:
    selector.close()
