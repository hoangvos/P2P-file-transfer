from tkinter import *
import tkinter as tk
import sys
import os
from tkinter import messagebox
from database import database
from model.Peer import Peer
from model.Peer import Peer_account
from model.File import File
from model import peer_repository
from model import file_repository
import uuid
import threading
import socket
from utils import shell_colors as shell
import tqdm
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox # pip install PyQt5
from PyQt5.Qt import QApplication as QApp
from tkinter import filedialog, messagebox
from service import handler
from tkinter import ttk
import multiprocessing
from ttkthemes import ThemedStyle
import re
import subprocess
from service.Server import HOST_SERVER, PORT_SERVER


CLIENT_COMMAND = "\n**** Invalid syntax ****\nFormat of client's commands\n1. publish lname fname\n2. fetch fname\n3. clear\n\n"
DOWNLOAD_COMMAND = "\n*** Invalid syntax ***\nTo download from source please follow the pattern\nfile_id session_id\n\n"

PUBLISH_PATTERN = r"^publish\s[a-zA-Z]:[\/\\](?:[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*[\/\\])*[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+$"
FETCH_PATTERN = r"^fetch\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"\\|,.<>\/?]*\.[A-Za-z0-9]+$"
FILE_ID_SESSION_ID_PATTERN = pattern = r"^[A-Z0-9]{16}\s[A-Z0-9]{16}$"
CLEAR_PATTERN = r"^clear$"



db_file = 'directory.db'

class App:
    def __init__(self, root, username, session_id):
        self.session_id = session_id
        self.root = root
        self.download_mode = False
        self.username = username
        self.root.title("User view")

        # Tạo đối tượng Notebook (các tab)
        self.notebook = ttk.Notebook(root)

        # Tạo và thêm các tab
        self.tab1 = tk.Frame(self.notebook)
        self.tab2 = tk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Home view")
        self.notebook.add(self.tab2, text="User CLI")
        self.create_tab2()

        # Đặt notebook vào cửa sổ chính
        self.notebook.grid(row=0, column=0, sticky="nsew")


        # Bắt sự kiện chuyển đổi tab
        self.notebook.bind("<ButtonRelease-1>", self.on_tab_click)

        # Áp dụng chủ đề từ ttkthemes
        style = ThemedStyle(root)
        style.set_theme("radiance")

        # Tạo kiểu tùy chỉnh để ẩn cạnh viền khi tab được chọn
        style.map("TNotebook.Tab", background=[('selected', 'lightblue')], borderwidth=[('selected', 0)])
    def on_tab_click(self, event):
        current_tab = self.notebook.index(self.notebook.select())
    def get_response(self, command):
        """
        Use for get response for each command and show it for user
        Return:
        response (String): The result when execute the command
        """
        message = None
        if command == "clear":
            return "clear"
        if re.search(PUBLISH_PATTERN, command):
            _, lname, fname = command.split(" ")
            message = f"ADDF_{fname}_{lname}_{self.session_id}"
            res = handler.serve(message.encode('utf-8'))
            if res.split()[0] == "AADD":
                return f"Successful upload {fname} !!!" 
            else:
                return "Can't upload {fname}"
        elif re.search(FETCH_PATTERN, command):
            _, fname = command.split(" ")
            message = f"FIND_{fname}_{self.session_id}"
            res = handler.serve(message.encode('utf-8'))
            return res
    def command_processing(self, command):
        """
        Return True when the command is in the correct format
        """
        if re.search(FETCH_PATTERN, command) or re.search(PUBLISH_PATTERN, command) \
            or re.search(CLEAR_PATTERN, command):
            return True
        return False
    def execute_command(self, input_field, output_field):
        """
        Used
        """
        command = input_field.get()
        input_field.delete(0, tk.END)
        output_field.config(state=tk.NORMAL)
        if self.download_mode:
            if not re.search(FILE_ID_SESSION_ID_PATTERN, command):
              output_field.insert(tk.END, DOWNLOAD_COMMAND, "color")
              output_field.see(tk.END)
            else:
              tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
              tmp_socket.connect((HOST_SERVER, PORT_SERVER))
              tmp_socket.send(f"POIF_{command.split()[-1]}_{command.split()[0]}".encode('utf-8'))
              peer_file = tmp_socket.recv('1024').decode('utf-8').split('_')

              client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
              client_socket.connect((peer_file[0], int(peer_file[1])))
              client_socket.send(f"Please send me {peer_file[2]} !!!".encode('utf-8')) 
              tmp_socket.close() 
              accept = client_socket.recv(1024).decode('utf-8')
              if accept == "True":
                client_socket.send(command.split()[0].encode('utf-8'))
                file_name = client_socket.recv(1024).decode('utf-8')
                output_field.insert(tk.END, f"\nFile name: {file_name}\n", "color")
                file_size = client_socket.recv(1024).decode('utf-8')
                output_field.insert(tk.END, f"\nFile size: {file_size}\n", "color")
                output_field.see(tk.END)
                file = open(peer_file[2], "wb")
                file_bytes = b""
                done = False
                pbar  = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size)) 
                while not done:
                  data = client_socket.recv(1024)
                  if file_bytes[-5:] == b"<END>":
                    done = True
                  else:
                    file_bytes += data
                  pbar.update(1024)
                pbar.close()
                file.write(file_bytes)
                file.close()
                output_field.insert(tk.END, f"\nSuccessful download {peer_file[2]} from {command.split()[-1]} !!!\n", "color")
                output_field.see(tk.END)
              else:
                output_field.insert(tk.END, f"\n{command.split()[-1]} don't permit you to download the file. Choose another source node !!!\n", "color")
                output_field.see(tk.END)
              client_socket.close()
              self.download_mode = False
                    
        else:
          output_field.insert(tk.END, f"{self.username}$ " + command + "\n", "color")

          if not self.command_processing(command):
              output_field.insert(tk.END, CLIENT_COMMAND, "color")
              output_field.see(tk.END)
          else:
              result = self.get_response(command)
              if command == "clear":
                  output_field.delete(0.1, tk.END)
                  output_field.insert(tk.END, 
                      "Terminal [Version 1.0.0]\nCopyright (C) hoang. All right reserved.\n\n", "color")
              elif command.split(" ")[0] == "publish":
                  output_field.insert(tk.END, f"\n{result}\n\n", "color")
                  output_field.see(tk.END)
              elif command.split(" ")[0] == "fetch":
                  if result[-3:] == "000":
                    output_field.insert(tk.END, f"\n{result}\n\n", "color")
                    output_field.insert(tk.END, "No file name {}")
                    output_field.see(tk.END)
                  else:
                    output_field.insert(tk.END, f"\n{result}\n\n", "color")
                    output_field.insert(tk.END, f"\nWhat source node you want to download from, following the pattern: file_id session_id\n\n", "color")
                    output_field.see(tk.END)
                    self.download_mode = True

                   

        output_field.config(state=tk.DISABLED)
    def create_tab2(self):
        header = tk.Label(self.tab2, text = f"Hello, {self.username}", font=("San Serif", 11, "bold"))
        header.grid(row = 0, column = 0, padx = 5, pady = 5)
        terminal_output = tk.Text(self.tab2, background = "black")
        terminal_output.tag_configure("color", foreground="white")
        terminal_output.insert(tk.END, "Terminal [Version 1.0.0]\nCopyright (C) hoang. All right reserved.\n\n", "color")
        terminal_output.config(state = tk.DISABLED)
        terminal_output.grid(row = 1, column = 0, columnspan = 89, padx = 5, pady = 5)

        input_header = tk.Label(self.tab2, text = ">>>")
        input_header.grid(row = 2, column = 0, sticky="e")

        input_field = tk.Entry(self.tab2)
        input_field.grid(row = 2, column = 1, columnspan = 89, sticky="we", padx = 5, pady = 10)

        input_field.bind('<Return>', lambda event: self.execute_command(input_field, terminal_output))  
