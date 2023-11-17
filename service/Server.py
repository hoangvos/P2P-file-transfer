#!/usr/bin/env python
import socket
import sys
import os
import multiprocessing
import threading
from . import handler
from utils import shell_colors as shell
import tkinter as tk
import re
from . import ServerFunctionCLI
from tkinter import ttk


db_file = 'directory.db'

SERVER_COMMAND = "\n**** Invalid syntax ****\nFormat of server's commands\n1. ping hostname\n2. discover hostname\n3. clear\n\n"
PING_PATTERN = r"^ping\s[\w]+$"
DISCOVER_PATTERN = r"^discover\s[\w]+$"
CLEAR_PATTERN = r"^clear$"

def run_x(opcode, hostname):
    """
    This method is used to run server's actions as PING and DISCOVER

    Parameters:
    - opcode: Code for PING or DISCOVER
    - hostname: Hostname of client

    Return:
    - str: Command output
    """
    output = None
    if opcode == 'PING':
        output = ServerFunctionCLI.PingHostname(hostname=hostname)
    elif opcode == 'DISCOVER':
        output = ServerFunctionCLI.DiscoverHostname(hostname=hostname)
    return output


def get_response(command):
    """
    Use for get response for each command and show it for user

    Return:
    response (String): The result when execute the command
    """
    if command == "clear":
        return "clear"
    opcode, hostname = command.split(" ")
    return run_x(opcode.upper(), hostname)

def command_processing(command):
    """
    Return True when the command is in the correct format
    """
    if re.search(PING_PATTERN, command) or re.search(DISCOVER_PATTERN, command) \
        or re.search(CLEAR_PATTERN, command):
        return True
    return False
def execute_command(input_field, output_field):
    command = input_field.get()
    output_field.config(state=tk.NORMAL)
    output_field.insert(tk.END, "\nServer$ " + command + "\n", "color")
    output_field.see(tk.END)
    input_field.delete(0, tk.END)

    if not command_processing(command):
        output_field.insert(tk.END, SERVER_COMMAND, "color")
        output_field.see(tk.END)
    else:
        result = get_response(command)
        if command == "clear":
            output_field.delete(0.1, tk.END)
            output_field.insert(tk.END, 
                "Terminal [Version 1.0.0]\nCopyright (C) hoang. All right reserved.\n\n", "color")
        else:
            output_field.insert(tk.END, result, "color")
            output_field.see(tk.END)

    output_field.config(state=tk.DISABLED)

def check(server_output, root):
	list_user = ServerFunctionCLI.getHostname() 
	for item in server_output.get_children():
		server_output.delete(item)
	for user in list_user:
		server_output.insert("", "end", values=(user[0], "Online" if user[1] == 1 else "Offline"))
	root.after(100, lambda: check(server_output, root))
	
def terminal(root):
	terminal_frame = tk.Frame(root)
	header = tk.Label(terminal_frame, text = f"SERVER RUN ...", 
											font=("San Serif", 11, "bold"))
	header.grid(row = 0, column = 0, padx = 5, pady = 5)
	terminal_output = tk.Text(terminal_frame, background = "black")
	terminal_output.tag_configure("color", foreground="white")
	terminal_output.insert(tk.END, "Terminal [Version 1.0.0]\nCopyright (C) hoang. All right reserved.\n\n", "color")     
	terminal_output.config(state = tk.DISABLED)
	terminal_output.grid(row = 1, column = 0, columnspan = 200, padx = 5, pady = 5)

	server_output = ttk.Treeview(terminal_frame, columns=("Column 1", "Column 2"), show="headings")	    
	server_output.grid(row=1, column = 200, columnspan = 10, padx = 5, pady = 5)
	server_output.heading("Column 1", text="User name")
	server_output.heading("Column 2", text="State")
	server_output.column("Column 1", anchor="center")
	server_output.column("Column 2", anchor="center")
	list_user = ServerFunctionCLI.getHostname()
	for user in list_user:
		server_output.insert("", "end", values=(user['username'], user['state_on_off']))
	root.after(100, lambda: check(server_output, root))
	input_header = tk.Label(terminal_frame, text = ">>>")
	input_header.grid(row = 2, column = 0, sticky="e")
	input_field = tk.Entry(terminal_frame)
	input_field.grid(row = 2, column = 1, columnspan = 199, sticky="we", pady = 5)
	input_field.bind('<Return>', lambda event: execute_command(input_field, terminal_output))
	return terminal_frame


class Server:
	def __init__(self, port: int):
		self.port = port
		self.ss = None
		self.BUFF_SIZE = 200

	def child(self, sd, clientaddr):
		try:
			(client, client_port) = socket.getnameinfo(clientaddr, socket.NI_NUMERICHOST)
			#self.ss.close()

			request = sd.recv(self.BUFF_SIZE)
			shell.print_green(f'{client} [{client_port}] -> ', end='')
			print(f'{request.decode("utf-8")}', end='')

			response = handler.serve(request)
			sd.send(response.encode("utf-8"))
			shell.print_red(' -> ', end='')
			print(f'{response}')

			if response[0:4] == "ALGO":
				shell.print_blue(f'Client {client} [{client_port}] said goodbye! {int(response[4:])} files deleted.')

			sd.close()
		except ConnectionResetError as e:

			sd.close()
			print("User log out")


	def __create_socket(self):
		try:
			# Create the socket
			self.ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except OSError as e:
			print(f'Can\'t create the socket: {e}')
			sys.exit(socket.error)
		try:
			# Set the SO_REUSEADDR flag in order to tell the kernel to reuse the socket even if it's in a TIME_WAIT state,
			# without waiting for its natural timeout to expire.
			# This is because sockets in a TIME_WAIT state can’t be immediately reused.
			#self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

			# Bind the local address (sockaddr) to the socket (ss)
			self.ss.bind(('10.229.74.245', self.port))

			# Transform the socket in a passive socket and
			# define a queue of SOMAXCONN possible connection requests
			self.ss.listen()
		except OSError:
			print(f'Can\'t handle the socket: {OSError}')
			sys.exit(socket.error)
	def run_gui(self):
		root = tk.Tk()
		tmp = terminal(root)
		tmp.pack()
		root.mainloop()

	def run(self):
		self.__create_socket()
		print(f'Server {self.ss.getsockname()[0]} listening on port {self.ss.getsockname()[1]}...')
		c = threading.Thread(target=self.run_gui)
		c.daemon = True
		c.start()
		while True:
			# Put the passive socket on hold for connection requests
			try:
				sd, clientaddr = self.ss.accept()
			except OSError as e:
				print(f'Error: {e}')
				sys.exit(socket.error)
			p = threading.Thread(target=self.child, args=(sd, clientaddr,))
			p.daemon = True
			p.start()
