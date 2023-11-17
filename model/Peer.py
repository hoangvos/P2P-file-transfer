#!/usr/bin/env python
from database import database
class Peer_account:
    def __init__(self,session_id, username, password):
        self.session_id = session_id 
        self.username = username
        self.password_account = password
    def insert(self, conn: database.sqlite3.Connection) -> None:
        """ Insert the peer into the db
        Parameters:
            conn - the db connection
        Returns:
            None
        """
        params = (self.session_id, self.username, self.password_account)
        conn.execute('INSERT INTO peers_account VALUES (?,?,?)', params)
    def delete(self, conn: database.sqlite3.Connection) -> None:
        """ Delete the peer from the db
        Parameters:
            conn - the db connection
        Returns:
            None
        """
        conn.execute('DELETE FROM peers_account WHERE session_id = ?', (self.session_id,))
class Peer:
    def __init__(self, session_id, ip, your_name, port, state_on_off):
        self.session_id = session_id
        self.ip = ip
        self.your_name = your_name
        self.port = port
        self.state_on_off = state_on_off
    def insert(self, conn: database.sqlite3.Connection) -> None:
        """ Insert the peer into the db
        Parameters:
            conn - the db connection
        Returns:
            None
        """
        params = (self.session_id, self.ip, self.your_name, self.port, self.state_on_off)
        conn.execute('INSERT INTO peers VALUES (?,?,?,?,?)', params)
    def delete(self, conn: database.sqlite3.Connection) -> None:
        """ Delete the peer from the db
        Parameters:
            conn - the db connection
        Returns:
            None
        """
        conn.execute('DELETE FROM peers WHERE session_id = ?', (self.session_id,))
        
    def update(self, conn: database.sqlite3.Connection) -> None:
        """ Update the peer into the db
        Parameters: 
            conn - the db connection
        Returns:
            None
        """
        query = """UPDATE peers
        SET port=:port, ip=:ip, your_name=:your_name, state_on_off=:state_on_off
        WHERE session_id =:session_id"""
        
        conn.execute(query, {'port': self.port, 'ip': self.ip, 'your_name': self.your_name, 'session_id':self.session_id,'state_on_off':self.state_on_off})