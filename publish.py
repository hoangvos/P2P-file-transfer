import socket
import sys 
from utils import shell_colors
import re

PUBLISH_PATTERN = r"^publish.py\s[a-zA-Z]:[\/\\](?:[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*[\/\\])*[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+$"
SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\npublish lname fname\n"

command = " ".join(sys.argv)
if re.search(PUBLISH_PATTERN, command):    
  host = "127.0.0.1"
  port = 3001
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((host, port))

  client_socket.send(f"publish {sys.argv[1]} {sys.argv[2]}".encode('utf-8'))
  shell_colors.print_green(client_socket.recv(1024).decode('utf-8'))
  client_socket.close() 
else:
  shell_colors.print_red(SERVER_COMMAND)




