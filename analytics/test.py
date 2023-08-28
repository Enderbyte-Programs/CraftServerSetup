import socket
import platform

s = socket.socket()
#s.connect(('enderbyteprograms.ddnsfree.com',11111))
s.connect(('enderbyteprograms.ddnsfree.com',11111))
s.sendall(f"GET /api/amcs/os={platform.platform()}&ver=0.12.2 HTTP/1.1".encode())
s.close()