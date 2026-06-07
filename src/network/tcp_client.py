import socket

from config.network import HOST, PORT

def connect_to_central():
    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect((HOST, PORT))
    client.setblocking(False)

    return client