import socket
import sys 
from utils import shell_colors
host = "127.0.0.1"
port = 3001
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

client_socket.send(f"publish {sys.argv[1]} {sys.argv[2]}".encode('utf-8'))
shell_colors.print_green(client_socket.recv(1024).decode('utf-8'))
client_socket.close() 




