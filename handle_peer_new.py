from tkinter import *
import tkinter as tk
import sys
import os
import pickle
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
from service.Server import PORT_SERVER, HOST_SERVER
from tkinter import ttk
import multiprocessing
from ttkthemes import ThemedStyle
import re
import subprocess 
import struct


CLIENT_COMMAND = "\n**** Invalid syntax ****\nFormat of client's commands\n1. publish lname fname\n2. fetch fname\n3. clear\n\n"
DOWNLOAD_COMMAND = "\n*** Invalid syntax ***\nTo download from source please follow the pattern\nfile_id session_id\n\n"


FILE_ID_SESSION_ID_PATTERN = pattern = r"^[A-Z0-9]{16}\s[A-Z0-9]{16}$"
CLEAR_PATTERN = r"^clear$"



db_file = 'directory.db'


def save_peer(root, session_id, ip, your_name, port):
  my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  my_socket.connect((HOST_SERVER, PORT_SERVER))
  my_socket.send(f"SAPE_{session_id}_{your_name}_{port}_{False}".encode('utf-8'))
  re_mess = my_socket.recv(1024).decode('utf-8')
  my_socket.close()
  root.destroy()
  login()

def show_account_info(session_id: str):
    # Tạo cửa sổ nhập thông tin tài khoản
    account_info_window = tk.Tk()
    account_info_window.title("Thông tin tài khoản")

    style = ttk.Style()
    style.configure('TButton', font=('calibri', 12, 'bold'), borderwidth='4')
    
    frame = ttk.Frame(account_info_window, padding="20")
    frame.grid(row=0, column=0, padx=50, pady=50)

    username_label = ttk.Label(frame, text="Tên của bạn:", font=('calibri', 12, 'bold'))
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    username_entry = ttk.Entry(frame, font=('calibri', 12))
    username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    port_label = ttk.Label(frame, text="Source port:", font=('calibri', 12, 'bold'))
    port_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

    port_entry = ttk.Entry(frame, font=('calibri', 12))
    port_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

    close_button = ttk.Button(frame, text="Lưu thông tin", command=lambda: save_peer(account_info_window, session_id=session_id, ip=socket.gethostbyname(socket.gethostname()), your_name=username_entry.get(), port=port_entry.get()))
    close_button.grid(row=2, column=0, columnspan=2, pady=20)

    # Bắt đầu vòng lặp chính của cửa sổ nhập thông tin tài khoản
    account_info_window.mainloop()





def register_user(root, username: str, password: str, password_rep: str) :
    if username and password and password_rep:
        if(password_rep != password):
            messagebox.showerror("Lỗi", "Mật khẩu không khớp !")
        else:
          my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
          my_socket.connect((HOST_SERVER, PORT_SERVER))
          my_socket.send(f"REGU_{username}_{password}".encode('utf-8'))
          re_mess = my_socket.recv(1024).decode('utf-8')
          if re_mess == "Error":
            messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại, vui lòng chọn tên khác.")
          else:
            session_id = re_mess.split('_')[1]
            message = f"Đăng ký tài khoản thành công!\nTên tài khoản: {username}\nMật khẩu: {password}"
            messagebox.showinfo("Đăng ký thành công", message)
            root.destroy()
            show_account_info(session_id=session_id)
          my_socket.close()
    else:
        messagebox.showerror("Lỗi", "Vui lòng điền cả tên tài khoản và mật khẩu.")


def register(root):
    root.destroy()
    register_root = tk.Tk()
    register_root.title("Đăng ký tài khoản")

    style = ttk.Style()
    style.configure('TButton', font=('calibri', 14, 'bold'), borderwidth='4')

    frame = ttk.Frame(register_root, padding="20")
    frame.grid(row=0, column=0, padx=50, pady=50)

    username_label = ttk.Label(frame, text="Tên tài khoản:", font=('calibri', 14, 'bold'))
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    username_entry = ttk.Entry(frame, font=('calibri', 14))
    username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    password_label = ttk.Label(frame, text="Mật khẩu:", font=('calibri', 14, 'bold'))
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

    password_entry = ttk.Entry(frame, show="*", font=('calibri', 14))
    password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

    password_rep_label = ttk.Label(frame, text="Nhập lại mật khẩu:", font=('calibri', 14, 'bold'))
    password_rep_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

    password_rep_entry = ttk.Entry(frame, show="*", font=('calibri', 14))
    password_rep_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

    register_button = ttk.Button(frame, text="Đăng ký", command=lambda: register_user(register_root, username=username_entry.get(), password=password_entry.get(), password_rep=password_rep_entry.get()))
    register_button.grid(row=3, column=0, columnspan=2, pady=20)

    register_root.mainloop()

def main_view(session_id:str):
  def add_file_to_list():
    file_path = filedialog.askopenfilename()  # Hiển thị hộp thoại mở tệp và lấy đường dẫn tệp đã chọn
    if file_path:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        my_socket.connect((HOST_SERVER, PORT_SERVER))
        my_socket.send(f"ADDF${file_path.split('/')[-1]}${file_path}${session_id}".encode('utf-8'))
        my_socket.recv(1024).decode('utf-8')
        my_socket.close()
  def check(treeview, session_id):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST_SERVER, PORT_SERVER))
    my_socket.send(f"GELI_{session_id}".encode('utf-8'))

    file_list = pickle.loads(my_socket.recv(4096))
    for item in treeview.get_children():
      treeview.delete(item)
    for file in file_list:
      treeview.insert("", "end", values=(file['file_name'], file['file_path'], file['file_md5']))
    tab1.after(100, lambda: check(treeview=treeview,session_id=session_id))
  def find_source_files(treeview, message):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST_SERVER, PORT_SERVER))
    my_socket.send(message)
    list_source = pickle.loads(my_socket.recv(4096))
    for item in treeview.get_children():
      treeview.delete(item)
    treeview.grid(row=3, column= 0, padx= 0, pady= 0)
    treeview.heading("Column 1", text="File name")
    treeview.heading("Column 2", text="File ID")
    treeview.heading("Column 3", text="Name")
    treeview.heading("Column 4", text="IP Address")
    treeview.heading("Column 5", text="Port")
    treeview.column("Column 1", anchor="center")
    treeview.column("Column 2", anchor="center")
    treeview.column("Column 3", anchor="center")
    treeview.column("Column 4", anchor="center")
    treeview.column("Column 5", anchor="center")
    if list_source:
      for source in list_source:
        if source['state_on_off']:
          treeview.insert("", "end",
              values=(source['file_name'],
                      source['file_md5'],
                      source['your_name'],
                      source['ip'],
                      source['port']))

  def download_from_source(event):
    selected_item = treeview_x.focus()
    values = treeview_x.item(selected_item, 'values')
    if values:
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
      HOST_download = values[3]
      PORT_download = int(values[4])
      print(HOST_download, PORT_download)
      client_socket.connect((HOST_download, PORT_download))
      client_socket.send(f"Please send me {values[0]} !!!".encode('utf-8')) 
      accept = client_socket.recv(1024).decode('utf-8')
      if accept == "True":
        client_socket.send(values[1].encode('utf-8'))
        file_name = client_socket.recv(1024).decode('utf-8')
        print(f"File name: {file_name}")
        file_size_bytes = client_socket.recv(8)
        file_size = struct.unpack("!Q", file_size_bytes)[0]

        print(f"File size: {file_size}")

        file = open(file_name, "wb")
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
        success_label = tk.Label(root, text="Successful download!", font=("Roboto", 24))
        success_label.grid(row=4, column=0, padx=10, pady=10)
        file.write(file_bytes)
        file.close()
        root.after(1000,lambda: success_label.destroy())
      client_socket.close()

  my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  my_socket.connect((HOST_SERVER, PORT_SERVER))
  
  my_socket.send(f"GELI_{session_id}".encode('utf-8'))
  file_list = pickle.loads(my_socket.recv(4096))
  my_socket.close() 

  # Tạo cửa sổ chính
  my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  my_socket.connect((HOST_SERVER, PORT_SERVER))
  my_socket.send(f"GENA_{session_id}".encode('utf-8'))
  username = my_socket.recv(1024).decode('utf-8')
  my_socket.close() 

  root = tk.Tk()
  root.title("User view")
  notebook = ttk.Notebook(root)
  tab1 = tk.Frame(notebook)
  notebook.add(tab1, text="Home view")
  notebook.grid(row=0, column=0, sticky="nsew")
  style = ThemedStyle(root)
  style.set_theme("radiance")
  # Tạo danh sách và đặt nó vào cửa sổ
  treeview = ttk.Treeview(tab1, columns=("Column 1", "Column 2", "Column 3"), show="headings")
  treeview_x = ttk.Treeview(tab1, columns=("Column 1", "Column 2", 'Column 3', 'Column 4', 'Column 5'), show="headings")
  treeview.grid(row=0, column= 0, padx= 0, pady= 0)
    # Đặt tên cho các cột
  treeview.heading("Column 1", text="File name")
  treeview.heading("Column 2", text="File path")
  treeview.heading("Column 3", text="File ID")
  # Cấu hình căn giữa cho mỗi cột
  treeview.column("Column 1", anchor="center")
  treeview.column("Column 2", anchor="center")
  treeview.column("Column 3", anchor="center")
  for file in file_list:
    treeview.insert("", "end", values=(file['file_name'], file['file_path'], file['file_md5']))

  tab1.after(100, lambda: check(treeview=treeview,session_id=session_id))
  # Tạo nút để chọn tệp và thêm vào danh sách
  add_file_button = tk.Button(tab1, text="Add File", command=add_file_to_list)
  add_file_button.grid(row=1, column=0, padx=10, pady=10)
  frame = tk.Frame(tab1)
  frame.grid(row=2, column=0, padx=10, pady=10)
  seek_file = tk.Label(frame, text="Nhập file :")
  seek_file.grid(row=1, column=0, padx=10, pady=10)
  seek_file_entry = tk.Entry(frame)
  seek_file_entry.grid(row=2, column=0, padx=10, pady=10)

  submit_button = tk.Button(frame, text="Submit", command=lambda: find_source_files(treeview=treeview_x,
    message=f'FINX_{seek_file_entry.get()}_{session_id}'.encode('utf-8')
  ))
  submit_button.grid(row=2, column=1)
  treeview_x.bind('<<TreeviewSelect>>', download_from_source)
  exit_button = tk.Button(root, text='Log out', command= lambda: sys.exit(0))
  exit_button.grid(row=5,column=0,padx=10, pady=10)
  # Bắt đầu vòng lặp chính của ứng dụng
  root.mainloop()




def user_cli(session_id:str):
  host = '127.0.0.1'
  port = 3001
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind((host, port))
  server_socket.listen(1)
  while True:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST_SERVER, PORT_SERVER))
    conn, addr = server_socket.accept()
    userInput = conn.recv(1024).decode('utf-8')
    cmd = userInput.split()[0]
    if cmd == "publish":
      path = userInput.split()[1]
      path = path.replace("\\", "/")
      mess =f"ADDF${userInput.split()[2]}${path}${session_id}"
      print(mess)
      my_socket.send(mess.encode('utf-8'))
      rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
      shell.print_red(rcv_message)
      if rcv_message.split()[0] == "AADD":
        conn.send(f"Successful upload {path}".encode('utf-8'))
    elif cmd == "fetch":
      my_socket.send(f"FIND_{userInput.split()[1]}_{session_id}".encode('utf-8'))
      rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
      shell.print_red(rcv_message)
      if rcv_message[-3:] != "000":
        conn.send(rcv_message.encode('utf-8')) 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command = conn.recv(1024).decode('utf-8')

        tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        tmp_socket.connect((HOST_SERVER, PORT_SERVER))
        tmp_socket.send(f"POIF_{command.split()[-1]}_{command.split()[0]}".encode('utf-8'))
        peer_file = tmp_socket.recv(1024).decode('utf-8').split('_')
        
        client_socket.connect((peer_file[0], int(peer_file[1])))
        client_socket.send(f"Please send me {peer_file[2]} !!!".encode('utf-8'))
        tmp_socket.close() 


        accept = client_socket.recv(1024).decode('utf-8')
        if accept == "True":
          client_socket.send(command.split()[0].encode('utf-8'))
          file_name = client_socket.recv(1024).decode('utf-8')
          print(f"File name: {file_name}")
          file_size_bytes = client_socket.recv(8)
          file_size = struct.unpack("!Q", file_size_bytes)[0]
          print(f"File size: {file_size}")

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
          conn.send(f"Successful download {peer_file[2]} from {command.split()[-1]} !!!\n".encode('utf-8'))
          client_socket.close()
      else:
        conn.send(f"No file name {userInput.split()[1]} !!!".encode('utf-8'))
        
    conn.close()
    my_socket.close()

def show_dialog(message:str, client_address:str):
    app = QApplication(sys.argv)
    message = f"Message from {client_address} : {message}. Do you want to accept it ?"
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Question)
    dialog.setText(message)
    dialog.setWindowTitle("Question")
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = dialog.exec()
    if result == QMessageBox.Yes:
        return True 
    elif result == QMessageBox.No:
        return False
    else:
        print("Dialog closed or an error occurred")
def source_node(session_id:str):
  tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  tmp_socket.connect((HOST_SERVER, PORT_SERVER))
  tmp_socket.send(f"POIP_{session_id}".encode('utf-8'))
  ip_port = tmp_socket.recv(1024).decode('utf-8').split('_')
  SOURCE_PORT = ip_port[1] 
  SOURCE_HOST = ip_port[0]
  tmp_socket.close()

  def child(client_socket, file_path):
    with open(file_path, 'rb') as f:
      file_size = os.path.getsize(file_path)
      file_size_bytes = struct.pack("!Q", file_size)
      file_name = file_path.split('/')[-1]
      client_socket.send(file_name.encode('utf-8'))
      client_socket.sendall(file_size_bytes)

      data = f.read()
      client_socket.sendall(data)
      client_socket.send(b"<END>")
      client_socket.close()


  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((SOURCE_HOST, int(SOURCE_PORT)))
  server.listen()

  while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address}")
    request = client_socket.recv(1024).decode('utf-8')
    if request == "PING":
      client_socket.send("Successful !!!".encode('utf-8'))
      client_socket.close()
    else:
      result = messagebox.askyesno("Flash Message", f"Request: {request}. Do you want to accept it?")
      if(result):
        client_socket.send(str(result).encode('utf-8'))
        file = client_socket.recv(1024).decode('utf-8')
        tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        tmp_socket.connect((HOST_SERVER, PORT_SERVER))
        tmp_socket.send(f"FIPA_{session_id}_{file}".encode('utf-8'))
        file_path = tmp_socket.recv(1024).decode('utf-8')
        print(file_path)
        if(file):
          t = threading.Thread(target=child, args=(client_socket, file_path,))
          t.daemon = True
          t.start()
        else:
          client_socket.close()
      else:
        client_socket.close()
    

def logic(root, username:str, password:str):
  my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  my_socket.connect((HOST_SERVER, PORT_SERVER))
  my_socket.send(f"LOGU_{username}_{password}".encode('utf-8'))
  
  res_message = my_socket.recv(1024).decode('utf-8')
  my_socket.close()
  if res_message == "Error":
    messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không đúng !")
  else:
    root.destroy()
    thread2 = threading.Thread(target=main_view, args=(res_message.split('_')[1],))
    thread1 = threading.Thread(target=user_cli, args=(res_message.split('_')[1],))
    thread3 = threading.Thread(target=source_node, args=(res_message.split('_')[1],))
  
    thread1.daemon = True
    thread3.daemon = True
    
    thread2.start() 
    thread1.start()
    thread3.start()   
    thread2.join()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST_SERVER, PORT_SERVER))
    my_socket.send(f"LOGX_{username}_{password}".encode('utf-8'))
    res_message = my_socket.recv(1024).decode('utf-8')
    my_socket.close()
       
   
def login():
    root = tk.Tk()
    root.title("Đăng nhập")

    style = ttk.Style()
    style.configure('TButton', font=('calibri', 14, 'bold'), borderwidth='4')

    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, padx=50, pady=50)

    username_label = ttk.Label(frame, text="Username:", font=('calibri', 14, 'bold'))
    username_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    username_entry = ttk.Entry(frame, font=('calibri', 14))
    username_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

    password_label = ttk.Label(frame, text="Password:", font=('calibri', 14, 'bold'))
    password_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

    password_entry = ttk.Entry(frame, show="*", font=('calibri', 14))
    password_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

    login_button = ttk.Button(frame, text="Sign in", command=lambda: logic(root, username=username_entry.get(), password=password_entry.get()))
    login_button.grid(row=2, column=0, columnspan=2, pady=20)

    signup_button = ttk.Button(frame, text="Sign up", command=lambda: register(root=root))
    signup_button.grid(row=3, column=0, columnspan=2, pady=10)



    root.mainloop()

login()