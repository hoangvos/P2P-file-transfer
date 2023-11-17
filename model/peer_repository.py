#!/usr/bin/env python
from database import database
from .Peer import Peer
from .Peer import Peer_account


def find_account(conn: database.sqlite3.Connection, username: str) -> 'Peer_account':
	""" Retrieve the peer with the given session_id
	Parameters:
		conn - the db connection
		session_id - session id for a peer
	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers_account WHERE username = ?', (username,))
	row = c.fetchone()
	if row is None:
		return None 
	peer_account = Peer_account(row['session_id'], username, row['password_account'])
	return peer_account

def find_account_by_session_id(conn: database.sqlite3.Connection, session_id: str) -> 'Peer_account':
	""" Retrieve the peer with the given session_id
	Parameters:
		conn - the db connection
		session_id - session id for a peer
	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers_account WHERE session_id = ?', (session_id,))
	row = c.fetchone()
	if row is None:
		return None 
	peer_account = Peer_account(session_id, row['username'], row['password_account'])
	return peer_account

def find(conn: database.sqlite3.Connection, session_id: str) -> 'Peer':
	""" Retrieve the peer with the given session_id
	Parameters:
		conn - the db connection
		session_id - session id for a peer
	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE session_id = ?', (session_id,))
	row = c.fetchone()
	if row is None:
		return None
	peer = Peer(session_id, row['ip'], row['your_name'], row['port'], row['state_on_off'])
	return peer


def find_by_ip_and_name(conn: database.sqlite3.Connection, ip: str, your_name: str) -> 'Peer':
	""" Retrieve the peer with the given session_id
	Parameters:
		conn - the db connection
		session_id - session id for a peer
	Returns:
		peer - first matching result for the research
	"""
	c = conn.cursor()
	c.execute('SELECT * FROM peers WHERE ip = ? AND your_name = ?', (ip, your_name))
	row = c.fetchone()
	if row is None:
		return None
	peer = Peer(row['session_id'], ip, your_name , row['port'], row['state_on_off'])
	return peer

def file_unlink(conn: database.sqlite3.Connection, session_id: str, file_md5: str) -> bool:
	""" Unlink the peer with the given session_id from the file
	Parameters:
		conn - the db connection
		session_id - session id for a peer
		file_md5 - md5 hash of a file
	Returns:
		bool - true or false either if it succeds or fails
	"""
	c = conn.cursor()
	c.execute('DELETE FROM files_peers WHERE file_md5 = ? AND session_id = ?', (file_md5, session_id,))


def get_peers_by_file(conn: database.sqlite3.Connection, file_md5: str) -> list:
	""" Retrieve all the peers that have the given file
		Parameters:
			conn - the db connection
			query - keyword for the search
		Returns:
			peers list - the list of corresponding peers
	"""
	c = conn.cursor()

	c.execute(
		'SELECT p.session_id, p.ip, p.your_name, p.port, p.state_on_off '
		'FROM peers AS p NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.file_md5 = ? AND p.state_on_off = ?',
		(file_md5,1)
	)
	peer_rows = c.fetchall()
	return peer_rows

def get_files_by_peer(conn: database.sqlite3.Connection, session_id: str) -> list:
	""" Retrieve all the peers that have the given file
		Parameters:
			conn - the db connection
			query - keyword for the search
		Returns:
			peers list - the list of corresponding peers
	"""
	c = conn.cursor()

	c.execute(
		'SELECT f.file_md5, f.file_name, f.file_path '
		'FROM files AS f NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.session_id = ?',
		(session_id,)
	)
	peer_rows = c.fetchall()
	return peer_rows

def get_files_by_peer_and_file_ID(conn: database.sqlite3.Connection, session_id: str, file_md5: str) -> list:
	""" Retrieve all the peers that have the given file
		Parameters:
			conn - the db connection
			query - keyword for the search
		Returns:
			peers list - the list of corresponding peers
	"""
	c = conn.cursor()

	c.execute(
		'SELECT f.file_md5, f.file_name, f.file_path '
		'FROM files AS f NATURAL JOIN files_peers AS f_p '
		'WHERE f_p.session_id = ? AND f_p.file_md5 = ?',
		(session_id,file_md5,)
	)
	peer_rows = c.fetchall()
	return peer_rows