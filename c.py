# This program in its current form does the following:
# The client process takes in a node list as an argument upon startup
# It cross-references this node list against a database of host names 
# It identifies the correct node to pass the rest of the node list to
# It contacts the (always on) server process of the node in question and establishes a TCP connection
# It sends the node list to the server

import sys # among other things, because we are reading arguments from the console upon startup
import socket # for socket programming
import selectors # to enable multiple connections asynchronously 
import types # ? cant remember why this is needed

sel = selectors.DefaultSelector()
messages = [b"RSU client process online.", "", ""] # two extra message slots to store the (length-2) node list

# parameters: host = the host name (IP address) of the server we want to connect to 
#             port = the server port number we want to write to 
#             num_conns = the number of connections we want to establish with the server socket
def start_connections(host, port):
    server_address = (host, port) # store the server IP address and port number to a server_addr object
    print(f"Starting connection to {server_address}")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket for a TCP connection
    client_socket.setblocking(False) # set this socket to non-blocking mode
    client_socket.connect_ex(server_address) # connect this new socket to the server socket. -- connect_ex() only initally produces an error indicator as opposed to a full blown exception if connect() is used

    events = selectors.EVENT_READ | selectors.EVENT_WRITE # client needs to know when the server is ready for both reading and writing and thus a bitwise OR operation is necessary
    
    # the data we want to store with the new socket is stored to a data object using SimpleNamespace
    data = types.SimpleNamespace( 
        server_id = server_address,
        msg_total=sum(len(m) for m in messages), # length of the message
        recv_total=0, # total number of messages received from the server
        messages=messages.copy(), # messages that the client will send to the server are copied because each connection will call socket.send() and modify the list (this can possibly be removed in our implementation?)
        outb=b"",
        ) # everything needed to keep track of what the client needs to send, has sent and has received, including the total number of bytes in the messages, is stored in the data object
    sel.register(client_socket, events, data=data) # once the new client socket has been created, connected to the server, and had its data object created, register it with the selector


def service_connection(key, mask):
    server_socket = key.fileobj # sock now represents the server socket object
    data = key.data # data now represents the data object associated with the socket object

    if mask & selectors.EVENT_READ: # if the mask and selectors.EVENT_READ both evaluate to true, then the server socket is ready for READING (from)
        recv_data = server_socket.recv(1024)  # read data in from the server
        if recv_data: # if data is successfully read in
            print(f"Received {recv_data!r} from {data.server_id}") 
            data.recv_total += len(recv_data) # increment the count of the data read in from the server
        #if not recv_data or data.recv_total == data.msg_total: # if no data received from the server or if the message received is an echo back (at least I think this is what's going on here)
        if not recv_data: # if no data received from the server or if the message received is an echo back (at least I think this is what's going on here)
            print(f"Closing connection with {data.server_id}")
            sel.unregister(server_socket) # unregister the server socket from the selector
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

# four possible destination nodes from our start point (recall city block model)
if sys.argv[2] == "A":
    host = "127.0.0.1"
    port = "33500"      
if sys.argv[2] == "C":
    host = "127.0.0.2"
    port = "33500"
if sys.argv[2] == "D":
    host = "127.0.0.3"
    port = "33500"    
if sys.argv[2] == "E":
    host = "127.0.0.4"
    port = "33500"  

messages[1] = str.encode(sys.argv[2])
messages[2] = str.encode(sys.argv[3])

start_connections(host, int(port)) # instead of listening for connections (server) the client begins by initiating connections via a start_connections() subroutine


try:
    while True:
        events = sel.select(timeout=1)
        if events: # if a server event has occurred (i.e. if connected to the server)
            for key, mask in events:
                service_connection(key, mask) # service the server connection
        # Check for a socket being monitored to continue.
        if not sel.get_map(): # if there is no connection to a server, break
            break
except KeyboardInterrupt:
    print("Client process terminated.")
finally:
    sel.close()
