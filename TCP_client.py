import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT1 = 33500  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # the client creates a socket object named s 
    print ("RSU 2 client process online.")
    s.connect((HOST, PORT1)) # the client knows the IP address and port it needs to connect to the server and simply inputs these to the connect() function
    s.sendall(b"Bus en route!") # the client uses sendall() to send its message to the server
    data = s.recv(1024) # it uses recv() to wait for a response from the server and when this message is received it closes the socket

print(f"From {HOST}: {data!r}") # the client prints the message that was echoed back by the server