#!/usr/bin/env python
import socket
import sys
import os
import multiprocessing
import threading
from utils import shell_colors as shell
import time
import tqdm
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox  # pip install PyQt5
from PyQt5.Qt import QApplication as QApp
import tkinter as tk
from tkinter import messagebox


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

def message_request(message:str, client_address:str):
  root = tk.Tk()
  message = f"Message from {client_address} : {message}. Do you want to accept it ?"
  result = messagebox.askquestion("Question", message, icon='question')
  choice = tk.StringVar()
  if result == 'yes':
      choice.set("Yes")
      root.destroy()
      return True 
  elif result == 'no':
      choice.set("No")
      root.destroy()
      return False
  else:
      choice.set("Cancel")
  # Run the main loop to display the dialog
  root.mainloop()

PORT = int(input("Input your port: "))

def thread1():
  HOST = '10.229.74.245'
  PORT_SERVER = 3000
  session = ""
  while True:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST, PORT_SERVER))
    if session != "":
      userInput = input(f"Session {session} : ")
      my_socket.send(f"{userInput}_{session}".encode('utf-8'))
    else:
      userInput = input()
      my_socket.send(userInput.encode('utf-8'))
    
    rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
    shell.print_red(rcv_message)
    if rcv_message[:4] == "ALGI":
      session = rcv_message[4:]
    elif rcv_message[:4] == "ADRE":
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
      HOST_download = input("Input source node ip you want to download : ")
      PORT_download = int(input("Input source node port you want to download : "))
      client_socket.connect((HOST_download, PORT_download))
      client_socket.send(f"Please send me {rcv_message.split(' ')[-1]}".encode('utf-8')) 
      file_name = client_socket.recv(1024).decode('utf-8')
      print(f"File name: {file_name}")
      file_size = client_socket.recv(1024).decode('utf-8')
      print(f"File size: {file_size}")

      file = open(file_name, "wb")
      file_bytes = b""
      done = False
      progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))
      while not done:
        data = client_socket.recv(1024)
        if file_bytes[-5:] == b"<END>":
          done = True
        else:
           file_bytes += data
        progress.update(1024)
      file.write(file_bytes)
      file.close()
      file.close()
    my_socket.close()
     


def thread2():
  HOST = socket.gethostbyname(socket.gethostname())
  
  def child(sd, file_path):
    file = open(file_path, 'rb')
    file_size = os.path.getsize(file_path)
    file_name = file_path.split('/')[-1]
    client_socket.send(file_name.encode('utf-8'))
    client_socket.send(str(file_size).encode('utf-8'))

    data = file.read()
    client_socket.sendall(data)
    client_socket.send(b"<END>")
    file.close()
    client_socket.close()


  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, PORT))
  server.listen()

  while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address}")
    request = client_socket.recv(1024).decode('utf-8')
    result = show_dialog(message=request, client_address=client_address)
    if(result):
      _, file = QApp(['./']), QFileDialog.getOpenFileName(parent=QWidget(), caption="Select file", directory='../')
      if(file):
        file_path = file[0]
        t = threading.Thread(target=child, args=(client_socket, file_path,))
        t.daemon = True
        t.start()
      else:
        client_socket.close()
    else:
      client_socket.close()



thread1 = threading.Thread(target=thread1)
thread2 = threading.Thread(target=thread2)

# Bắt đầu chạy các luồng

thread2.start()
thread1.start()
# Đợi cho tất cả các luồng hoàn thành

thread2.join()
thread1.join()