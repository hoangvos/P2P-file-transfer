import sqlite3
from prettytable import PrettyTable
from . import Server
import socket
import time

databaseDirectory = 'directory.db'

def DiscoverHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()

        headersTuple = ("Hostname","file_md5","file_name")

        if hostname == "":
            print("Hostname empty","Please enter a hostname")
            return

        queryString = "SELECT A.username, F.file_md5, F.file_name FROM peers_account AS A, peers AS P, files AS F, files_peers AS R WHERE A.session_id=P.session_id AND P.session_id=R.session_id AND F.file_md5=R.file_md5 AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        return PrintTable(headersTuple,outputRows)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()

def PingHostname(hostname):
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()

        headersTuple = ("Hostname","online_state")

        if hostname == "":
            print("Hostname empty","Please enter a hostname")
            return

        queryString = "SELECT A.username, P.state_on_off, P.ip, P.port FROM peers_account AS A, peers AS P WHERE A.session_id = P.session_id AND A.username=?"
        cursor.execute(queryString,(hostname,))
        outputRows = cursor.fetchall()
        if not outputRows:
            return f"No hostname like {hostname}"
        if outputRows[0][1] == 0:
            return f"{hostname} is not logged in yet"
        client_info = f"--Client--: {hostname}\n"
        try:
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            my_socket.connect((outputRows[0][2], int(outputRows[0][3])))
            my_socket.send("PING".encode('utf-8'))
            start_time = time.time()
            response = my_socket.recv(1024).decode('utf-8')
            end_time = time.time()
            round_trip_time = "{:,.8f}".format(end_time - start_time)
            if response:
                
                client_info += "--Status--: ALIVE\n"
                client_info += f"--Round-Trip Time--: {round_trip_time} (s)\n"
                return client_info
        except Exception as e:
            client_info += f"--Status--: NOT ALIVE\n"
            client_info += f"--Error--: {e}\n"
            return client_info
        
        return PrintTable(headersTuple,outputRows)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()


def getHostname():
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()

        queryString = "SELECT A.username, P.state_on_off FROM peers_account AS A, peers AS P WHERE A.session_id = P.session_id"
        cursor.execute(queryString)
        outputRows = cursor.fetchall()
        return outputRows
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()

def ShowAllUser():
    try:
        connection = sqlite3.connect(databaseDirectory)
        cursor = connection.cursor()

        headersTuple = ("session_id","ip","client_name","port","online_state","file_md5","file_name","download_count")

        queryString ="SELECT P.session_id, P.ip, P.your_name, P.port, P.state_on_off, F.file_md5, F.file_name, F.download_count FROM peers AS P, files AS F, files_peers AS R WHERE P.session_id=R.session_id AND F.file_md5=R.file_md5"
        cursor.execute(queryString)
        outputRows = cursor.fetchall()
        
        PrintTable(headersTuple,outputRows)
    except sqlite3.Error as error:
        print("Error while connecting to sqlite",error,"\n")
    finally:
        if connection:
            connection.close()

def PrintTable(headersTuple,outputRows):
    table = PrettyTable()
    table.field_names = headersTuple
    for row in outputRows:
        table.add_row(row)
    return table
