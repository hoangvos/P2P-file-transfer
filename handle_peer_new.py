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
from CLI_handle import App
import subprocess 


CLIENT_COMMAND = "\n**** Invalid syntax ****\nFormat of client's commands\n1. publish lname fname\n2. fetch fname\n3. clear\n\n"
DOWNLOAD_COMMAND = "\n*** Invalid syntax ***\nTo download from source please follow the pattern\nfile_id session_id\n\n"

PUBLISH_PATTERN = r"^publish\s[a-zA-Z]:[\/\\](?:[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*[\/\\])*[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]*\.[A-Za-z0-9]+$"
FETCH_PATTERN = r"^fetch\s[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"|,.<>?]+[\sa-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':\"\\|,.<>\/?]*\.[A-Za-z0-9]+$"
FILE_ID_SESSION_ID_PATTERN = pattern = r"^[A-Z0-9]{16}\s[A-Z0-9]{16}$"
CLEAR_PATTERN = r"^clear$"



db_file = 'directory.db'




def save_peer(root, session_id, ip, your_name, port):
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  peer = Peer(session_id=session_id, ip = ip, your_name = your_name, port = port, state_on_off=False)
  peer.insert(conn=conn)
  conn.commit()
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

    # Đưa cửa sổ ra giữa
    window_width = account_info_window.winfo_reqwidth()
    window_height = account_info_window.winfo_reqheight()
    position_right = int(account_info_window.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(account_info_window.winfo_screenheight() / 2 - window_height / 2)
    account_info_window.geometry("+{}+{}".format(position_right, position_down))

    # Bắt đầu vòng lặp chính của cửa sổ nhập thông tin tài khoản
    account_info_window.mainloop()





def register_user(root, username: str, password: str, password_rep: str) :
    if username and password and password_rep:
        if(password_rep != password):
            messagebox.showerror("Lỗi", "Mật khẩu không khớp !")
        else:
          try:
            conn = database.get_connection(db_file)
            conn.row_factory = database.sqlite3.Row
          except database.Error as e:
            print(f'Error: {e}')
          # Đây là nơi để xử lý việc lưu thông tin người dùng vào cơ sở dữ liệu hoặc tập tin
          # Trong ví dụ này, chúng ta chỉ hiển thị một thông báo
          peer_account = peer_repository.find_account(conn, username=username)
          if peer_account is not None:
            messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại, vui lòng chọn tên khác.")
          else:
            session_id = str(uuid.uuid4().hex[:16].upper())
            peer = peer_repository.find(conn, session_id)
            while peer is not None:
              session_id = str(uuid.uuid4().hex[:16].upper())
              peer = peer_repository.find(conn, session_id)
            peer_account = Peer_account(session_id=session_id, username=username, password=password)
            peer_account.insert(conn=conn)
            conn.commit()
            message = f"Đăng ký tài khoản thành công!\nTên tài khoản: {username}\nMật khẩu: {password}"
            messagebox.showinfo("Đăng ký thành công", message)
            root.destroy()
            show_account_info(session_id=session_id)
    else:
        messagebox.showerror("Lỗi", "Vui lòng điền cả tên tài khoản và mật khẩu.")


def register(root):
    root.destroy()
    register_root = tk.Tk()
    register_root.title("Đăng ký tài khoản")

    # Định nghĩa kiểu cho ttk.Button
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
          handler.serve(f"ADDF_{file_path.split('/')[-1]}_{file_path}_{session_id}".encode('utf-8'))
  def check(treeview, conn, session_id):
    file_list = peer_repository.get_files_by_peer(conn=conn, session_id=session_id)
    for item in treeview.get_children():
      treeview.delete(item)
    for file in file_list:
      treeview.insert("", "end", values=(file['file_name'], file['file_path'], file['file_md5']))
    app.tab1.after(100, lambda: check(treeview=treeview, conn=conn, session_id=session_id))
  def find_source_files(treeview, message):
    list_source = handler.find(message)
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
      client_socket.connect((HOST_download, PORT_download))
      client_socket.send(f"Please send me {values[0]} !!!".encode('utf-8')) 
      accept = client_socket.recv(1024).decode('utf-8')
      if accept == "True":
        client_socket.send(values[1].encode('utf-8'))
        file_name = client_socket.recv(1024).decode('utf-8')
        print(f"File name: {file_name}")
        file_size = client_socket.recv(1024).decode('utf-8')
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
      
 
 
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  file_list = peer_repository.get_files_by_peer(conn=conn, session_id=session_id)
  # Tạo cửa sổ chính
  username = peer_repository.find_account_by_session_id(conn=conn, session_id= session_id).username
  root = tk.Tk()
  app = App(root, username, session_id)
  # Tạo danh sách và đặt nó vào cửa sổ
  treeview = ttk.Treeview(app.tab1, columns=("Column 1", "Column 2", "Column 3"), show="headings")
  treeview_x = ttk.Treeview(app.tab1, columns=("Column 1", "Column 2", 'Column 3', 'Column 4', 'Column 5'), show="headings")
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

  app.tab1.after(100, lambda: check(treeview=treeview, conn=conn, session_id=session_id))
  # Tạo nút để chọn tệp và thêm vào danh sách
  add_file_button = tk.Button(app.tab1, text="Add File", command=add_file_to_list)
  add_file_button.grid(row=1, column=0, padx=10, pady=10)
  frame = tk.Frame(app.tab1)
  frame.grid(row=2, column=0, padx=10, pady=10)
  seek_file = tk.Label(frame, text="Nhập file :")
  seek_file.grid(row=1, column=0, padx=10, pady=10)
  seek_file_entry = tk.Entry(frame)
  seek_file_entry.grid(row=2, column=0, padx=10, pady=10)

  submit_button = tk.Button(frame, text="Submit", command=lambda: find_source_files(treeview=treeview_x,
    message=f'FIND_{seek_file_entry.get()}_{session_id}'.encode('utf-8')
  ))
  submit_button.grid(row=2, column=1)
  treeview_x.bind('<<TreeviewSelect>>', download_from_source)
  exit_button = tk.Button(root, text='Log out', command= lambda: sys.exit(0))
  exit_button.grid(row=5,column=0,padx=10, pady=10)
  # Bắt đầu vòng lặp chính của ứng dụng
  root.mainloop()




def user_cli(session_id:str):
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  host = '127.0.0.1'
  port = int(peer_repository.find(conn=conn, session_id=session_id).port)
  conn.close()
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.bind((host, port))
  server_socket.listen(1)
  HOST = '10.229.74.245'
  PORT_SERVER = 3000
  session = session_id
  while True:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST, PORT_SERVER))
    conn, addr = server_socket.accept()
    userInput = conn.recv(1024).decode('utf-8')
    cmd = userInput.split()[0]
    if cmd == "publish":
      my_socket.send(f"ADDF_{userInput.split()[1]}_{userInput.split()[2]}_{session_id}".encode('utf-8'))
      rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
      shell.print_red(rcv_message)
      if rcv_message.split()[0] == "AADD":
        conn.send(f"Successful upload {userInput.split()[2]}".encode('utf-8'))
    elif cmd == "fetch":
      my_socket.send(f"FIND_{userInput.split()[1]}_{session_id}".encode('utf-8'))
      rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
      shell.print_red(rcv_message)
      if rcv_message[-3:] != "000":
        conn.send(rcv_message.encode('utf-8')) 
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        command = conn.recv(1024).decode('utf-8')
        try:
          connn = database.get_connection(db_file)
          connn.row_factory = database.sqlite3.Row
        except database.Error as e:
          print(f'Error: {e}')
        peer = peer_repository.find(conn=connn, session_id=command.split()[-1])
        filename = file_repository.find(conn=connn, file_md5=command.split()[0]).file_name
        connn.close()
        client_socket.connect((peer.ip, int(peer.port)))
        client_socket.send(f"Please send me {filename} !!!".encode('utf-8')) 
        accept = client_socket.recv(1024).decode('utf-8')
        if accept == "True":
          client_socket.send(command.split()[0].encode('utf-8'))
          file_name = client_socket.recv(1024).decode('utf-8')
          print(f"File name: {file_name}")
          file_size = client_socket.recv(1024).decode('utf-8')
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
          file.write(file_bytes)
          file.close()
          client_socket.close()
          conn.send(f"Successful download {filename} from {command.split()[-1]} !!!\n".encode('utf-8'))
        else:
          conn.send(f"No file name {userInput.split()[1]} !!!")
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
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  PORT = peer_repository.find(conn=conn, session_id=session_id).port
  conn.close()
  HOST = socket.gethostbyname(socket.gethostname())
  def child(client_socket, file_path):
    with open(file_path, 'rb') as f:
      file_size = os.path.getsize(file_path)
      file_name = file_path.split('/')[-1]
      client_socket.send(file_name.encode('utf-8'))
      client_socket.send(str(file_size).encode('utf-8'))

      data = f.read()
      client_socket.sendall(data)
      client_socket.send(b"<END>")
      client_socket.close()


  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, int(PORT)))
  server.listen()

  while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address}")
    request = client_socket.recv(1024).decode('utf-8')
    result = messagebox.askyesno("Flash Message", f"Request: {request}. Do you want to accept it?")
    if(result):
      client_socket.send(str(result).encode('utf-8'))
      file = client_socket.recv(1024).decode('utf-8')
      try:
        conn = database.get_connection(db_file)
        conn.row_factory = database.sqlite3.Row
      except database.Error as e:
        print(f'Error: {e}')
      file_path = peer_repository.get_files_by_peer_and_file_ID(conn=conn, session_id=session_id, file_md5=file)[0][2]
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
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  peer_account = peer_repository.find_account(conn=conn, username=username)
  if peer_account is not None:
    if password == peer_account.password_account:
      peer = peer_repository.find(conn, peer_account.session_id)
      peer.ip = socket.gethostbyname(socket.gethostname())
      peer.state_on_off = True
      peer.update(conn)
      conn.commit()

      root.destroy()
      thread2 = threading.Thread(target=main_view, args=(peer_account.session_id,))
      thread1 = threading.Thread(target=user_cli, args=(peer_account.session_id,))
      thread3 = threading.Thread(target=source_node, args=(peer_account.session_id,))
   
      thread1.daemon = True
      thread3.daemon = True
      
      thread2.start() 
      thread1.start()
      thread3.start()   
      thread2.join()
      peer.state_on_off = False
      peer.update(conn)
      conn.commit()
      conn.close()

    else:
      messagebox.showerror("Lỗi", "Mật khẩu không đúng !")
  else:
    messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không đúng !")
       
   
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

    # Đưa cửa sổ ra giữa
    window_width = root.winfo_reqwidth()
    window_height = root.winfo_reqheight()
    position_right = int(root.winfo_screenwidth() / 2 - window_width / 2)
    position_down = int(root.winfo_screenheight() / 2 - window_height / 2)
    root.geometry("+{}+{}".format(position_right, position_down))

    root.mainloop()

login()
   