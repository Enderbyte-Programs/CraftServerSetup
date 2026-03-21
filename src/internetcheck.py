"""A library for checking if an internet connection exists"""

import socket

def is_computer_connected_to_internet() -> bool:
    try:
        socket.create_connection(("google.com",80))

    except:
        return False
    else:
        return True