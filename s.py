import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()

# takes a new socket object and registers it with the selector
# argument: new client socket object
# function: registers the new socket object with the selector
def accept_client(sock):
    conn, addr = sock.accept()  # listening socket has been registered for the event selectors.EVENT_READ so it should be ready to read (assuming the correct port number has been used by the client)
    print(f"Accepted connection from {addr}")
    conn.setblocking(False) # put events from this new socket in non-blocking mode
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"") # use SimpleNamespace to create an object to hold the data that you want included along with the socket
    # essentially this instantiates an object that can hold attributes and nothing else - like an empty class
    # =>i.e. create an object to store values as attributes without having to create a (almost empty) class.
    # note that data.inb is data READ from the client and data.outb is data WRITTEN to the client
    events = selectors.EVENT_READ | selectors.EVENT_WRITE # the server process needs to know when the client is ready for either reading OR writing and thus both of these events are set with the bitwise OR operator
    sel.register(conn, events, data=data) # pass the events socket, mask and data objects to sel.register to register this new client event with the selector  

# function to handle a client connection once it has been registered successfully
# arguments: key = namedtuple returned from .select() that contains the socket object (fileobj) and data object
#            mask = the events that are ready
# function: 
def service_connection(key, mask):
    sock = key.fileobj # sock now represents the client socket object
    data = key.data # data now represents the data object associated with the socket object
    if mask & selectors.EVENT_READ: # if the mask and selectors.EVENT_READ both evaluate to true, then the socket is ready for READING (from)
        recv_data = sock.recv(1024)  # read data in from the client
        if recv_data:
            data.outb += recv_data # any data read in is appended to data.outb to be sent back later (recall that this server echoes back to the clients)
        else:
            print(f"Closing connection to {data.addr}\n") # if no data is received then the client has closed their socket, so the server should too
            sel.unregister(sock) # first, unregister the dead client socket with the selector
            sock.close() # then close the connection to the client socket
            always_on()
    if mask & selectors.EVENT_WRITE: # if the mask and selectors.EVENT_WRITE both evaluate to true then the socket is ready for WRITING (to)
        if data.outb: # if there is any data stored in data.outb (i.e. if any data has been read in from the client socket, as we are immediately appending received data to data.outb)
            print(f"Echoing {data.outb!r} to {data.addr}") # echo any received and stored data back to the socket it originated from
            sent = sock.send(data.outb)  # .send() returns the number of bytes sent 
            data.outb = data.outb[sent:] # this value is then used with slice notation to discard the bytes sent from the data.outb buffer

def always_on():
    host  = sys.argv[1]   # read the host address and listening port number from terminal
    port = int(sys.argv[2])
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a new socket 
    
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    lsock.bind((host, port)) # bind it to the address and port number taken from the terminal
    lsock.listen() # listen for new connections
    print(f"Listening on {(host, port)}")
    lsock.setblocking(False) # calls to the socket will no longer block
    sel.register(lsock, selectors.EVENT_READ, data=None) # registers the listening socket to be monitored with sel.select()  
    # "data" is used to keep track of what has been sent and received on the socket

    try:
        while True:
            events = sel.select(timeout=None) # thanks to the non blocking socket set up, we can wait for events on multiple sockets and deal with them appropriately
            # lack of a timeout ensures that execution is blocked until there are sockets ready for i/o
            # events is returned a list of tuples, one for each socket, each containing a key and a mask
            # the key is a SelectorKey namedtuple that contains a fileobj attribute
            # key.fileobj is the socket object
            # mask is an event mask of the operations that are ready
            for key, mask in events:
                if key.data is None: # if there is no data, then you know it's from the listening socket and you need to accept the connection
                    accept_client(key.fileobj) # call a subroutine to get the new socket object and register it with the selector
                else: # if there is data, then you know this is a client object that has already been accepted 
                    service_connection(key, mask) # call the subroutine that services a pre-existing client socket
    except KeyboardInterrupt:
        print("Server process terminated.")
    finally:
        sel.close()
        always_on()

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

if sys.argv[1] == "127.0.0.1":
    node_id = "A"
if sys.argv[1] == "127.0.0.2":
    node_id = "B"
if sys.argv[1] == "127.0.0.3":
    node_id = "C"
if sys.argv[1] == "127.0.0.4":
    node_id = "D"
if sys.argv[1] == "127.0.0.5":
    node_id = "E"

print(f"RSU {node_id} server process initiated.")

always_on()
