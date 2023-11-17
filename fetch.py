import socket
import sys 
import re
FILE_ID_SESSION_ID_PATTERN = pattern = r"^[A-Z0-9]{16}\s[A-Z0-9]{16}$"
DOWNLOAD_COMMAND = "\n*** Invalid syntax ***\nTo download from source please follow the pattern\nfile_id session_id\n\n"

from utils import shell_colors
host = "127.0.0.1"
port = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

client_socket.send(f"fetch {sys.argv[1]}".encode('utf-8'))
message = client_socket.recv(2048).decode('utf8')
shell_colors.print_green(message)
if message.split()[0] == 'Number':
  source_choose = input("What source node you want to download from, following the pattern: file_id session_id \n")
  while not re.search(FILE_ID_SESSION_ID_PATTERN, source_choose):
    shell_colors.print_red(DOWNLOAD_COMMAND)
    source_choose = input(">>>>")
  client_socket.send(source_choose.encode('utf-8'))
  shell_colors.print_green(client_socket.recv(2048).decode('utf-8'))

client_socket.close() 

