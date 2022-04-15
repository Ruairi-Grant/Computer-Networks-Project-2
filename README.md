# 3D3_Project_2

Demonstration of RSU represented by node.py and s.py and of connecting client bus.py

To demo bus.py, and the RSU represented by server.py and node.py
1. Ensure the adresses in bus.py, node.py and server.py are all consistent and available on the devices.
1. In the first raspberry pi:run server.py and pass its host and port number to it: eg. python3 server.py 127.0.0.1 33500
2. In the same raspberry pi as above: run node.py 
3. From a second raspberry pi:  run bus.py A B C


This simulates the following:
- Node A's server process (which should be permanently running) starting up
- Node B takes a node list (which it has received via UDP from a bus) and identifies the next node that must be contacted (Node A)
- Node B then contacts node A via TCP and sends it the node list
- Node A echoes these messages back to Node B to as confirmation that they were received
- Node C then contacts A with a separate node list and the same procedure takes place
- The programs are terminated via keyboard interrupt (ctrl + c, ctrl + z, ctrl + fn + break, etc. depending on your computer)


