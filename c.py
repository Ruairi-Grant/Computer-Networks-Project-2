import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"Message 1 from client.", b"Message 2 from client."]

# parameters: host = the host name (IP address) of the server we want to connect to 
#             port = the server port number we want to write to 
#             num_conns = the number of connections we want to establish with the server socket
def start_connections(host, port, num_conns):
    server_addr = (host, port) # store the server IP address and port number to a server_addr object
    for i in range(0, num_conns): # for the number of connections specified
        connid = i + 1 # give each new connection a unique identifier
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket for a TCP connection
        sock.setblocking(False) # set this socket to non-blocking mode
        sock.connect_ex(server_addr) # connect this new socket to the server socket. -- connect_ex() only initally produces an error indicator as opposed to a full blown exception if connect() is used
        events = selectors.EVENT_READ | selectors.EVENT_WRITE # client needs to know when the server is ready for both reading and writing and thus a bitwise OR operation is necessary
        # the data we want to store with the new socket is stored to a data object using SimpleNamespace
        data = types.SimpleNamespace( 
            connid=connid, # connection number (this will be removed in our implementation)
            msg_total=sum(len(m) for m in messages), # length of the message
            recv_total=0, # total number of messages received from the server
            messages=messages.copy(), # messages that the client will send to the server are copied because each connection will call socket.send() and modify the list (this can possibly be removed in our implementation?)
            outb=b"",
        ) # everything needed to keep track of what the client needs to send, has sent and has received, including the total number of bytes in the messages, is stored in the data object
        sel.register(sock, events, data=data) # once the new client socket has been created, connected to the server, and had its data object created, register it with the selector


def service_connection(key, mask):
    sock = key.fileobj # sock now represents the server socket object
    data = key.data # data now represents the data object associated with the socket object
    if mask & selectors.EVENT_READ: # if the mask and selectors.EVENT_READ both evaluate to true, then the server socket is ready for READING (from)
        recv_data = sock.recv(1024)  # read data in from the server
        if recv_data: # if data is successfully read in
            print(f"Received {recv_data!r} from connection {data.connid}") 
            data.recv_total += len(recv_data) # increment the count of the data read in from the server
        if not recv_data or data.recv_total == data.msg_total: # if no data received from the server or if the message received is an echo back (at least I think this is what's going on here)
            print(f"Closing connection {data.connid}")
            sel.unregister(sock) # unregister the server socket from the selector
            sock.close() # close the connection to the server socket
        # V. IMPORTANT: 
        # THE KEY DIFFERENCE BETWEEN THE WAY THE SERVER HANDLES ITS CONNECTIONS AND THE WAY THIS CLIENT PROGRAM HANDLES CONNECTIONS IS THAT THE CLIENT KEEPS TRACK OF THE NUMBER OF BYTES IT HAS RECEIVED FROM THE SERVER
        # IF THE CLIENT DETECTS THAT IT HAS RECEIVED AN ECHO BACK FROM THE SERVER, IT CLOSES THE CONNECTION
        # ONCE THE CLIENT CLOSES ITS SIDE OF THE CONNECTION, THE SERVER DETECTS THAT THIS HAS OCCURRED (DUE TO THE ABSENCE OF NEW MESSAGES FROM THE CLIENT) AND FOLLOWS SUIT
    if mask & selectors.EVENT_WRITE: # if both true then the server socket is ready for WRITING to
        if not data.outb and data.messages: # if there is nothing to send
            data.outb = data.messages.pop(0)
        if data.outb: # if there is a message to send out
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # record the number of bytes sent
            data.outb = data.outb[sent:] # discard these bytes from the data out buffer 


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)

host, port, num_conns = sys.argv[1:4] # num_conns is the number of connections we want the client to create with the server and is read from the command line
# these two code files at present enable a client socket to establish multiple connections with ONE server
# we need a server that can maintain four connections to four separate client sockets#
#
# for our purposes, we only need one connection between a given client and server process, so this will need to be changed
# what we need is a server that can support four connections simultaneously with four client processes
# (RECALL CITY BLOCK MODEL)
# meaning that at all times a given RSU has ONE server process and FOUR client processes operating simultaneously

start_connections(host, int(port), int(num_conns)) # instead of listening for connections (server) the client begins by initiating connections via a start_connections() subroutine

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
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()