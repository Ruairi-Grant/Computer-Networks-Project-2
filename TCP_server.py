import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT1 = 33500  

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_socket:
    listen_socket.bind((HOST, PORT1))
    listen_socket.listen()
    print(f"RSU 1 TCP server process online. \nListening for incoming TCP connection on {(HOST, PORT1)}")
    conn, addr = listen_socket.accept()
    with conn:
        print(f"Connection established with {addr}")
        while True:
            data = conn.recv(1024)
            if data:
                print(f"Message received from {addr}: {data}")
                conn.sendall(b"Message received.")
