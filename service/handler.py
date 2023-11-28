#!/usr/bin/env python
from database import database
from model.Peer import Peer
from model.File import File
from model import peer_repository
from model import file_repository
import uuid
from model.Peer import Peer_account
import socket
import pickle

db_file = 'directory.db'

def serve(request: bytes, ip) -> str:
	""" Handle the peer request
	Parameters:
		request - the list containing the request parameters
	Returns:
		str - the response
	"""
	command = request[0:4].decode('UTF-8')
	if command == "ADDF":
		items = request.decode('utf-8')
		list_items = items.split('$')
		if len(list_items) != 4:
			return "Invalid request. Usage is: ADDF_<filename>_<filepath>_<your_session_id>"
		name = list_items[1]
		file_path = list_items[2]
		session_id = list_items[3]

		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		try:
			peer = peer_repository.find(conn, session_id)

			if peer is None:
				conn.close()
				return "Unauthorized: your SessionID is invalid"
			
			md5 = str(uuid.uuid4().hex[:16].upper())
			file = file_repository.find(conn, md5)
			while file is not None:
				
				md5 = str(uuid.uuid4().hex[:16].upper())
				file = file_repository.find(conn, md5)

			file = File(md5, name, file_path, 0)
			file.insert(conn)
			file_repository.add_owner(conn, md5, session_id)

			conn.commit()
			conn.close()

		except database.Error as e:
			conn.rollback()
			conn.close()
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."
		return f'AADD file with name {name} to repository'

	elif command == "DELF":
		items = request.decode('utf-8')
		list_items = items.split('_')
		if len(list_items) != 3:
			return "Invalid request. Usage is: DELF_<file_md5>_<your_session_id>"

		session_id = list_items[2]
		md5 = list_items[1]

		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row

		except database.Error as e:
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		try:
			peer = peer_repository.find(conn, session_id)

			if peer is None:
				conn.close()
				return "Unauthorized: your SessionID is invalid"

			if not file_repository.peer_has_file(conn, session_id, md5):
				conn.close()
				return "ADEL999"

			peer_repository.file_unlink(conn, session_id, md5)

			copy = file_repository.get_copies(conn, md5)

			if copy == 0:
				file = file_repository.find(conn, md5)
				file.delete(conn)

			conn.commit()
			conn.close()

		except database.Error as e:
			conn.rollback()
			conn.close()
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		return f"ADEL delete copies of {md5} from {session_id}" 

	elif command == "FIND":
		items = request.decode('utf-8')
		list_items = items.split('_')
		if len(list_items) != 3:
			return "Invalid command. Usage is: FIND_<query_string>_<your_session_id>"
		
		session_id = list_items[2]
		query = list_items[1]

		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row

		except database.Error as e:
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		try:
			peer = peer_repository.find(conn, session_id)

			if peer is None:
				conn.close()
				return "Unauthorized: your SessionID is invalid"

			total_file = file_repository.get_files_count_by_querystring(conn, query)
			if total_file == 0:
				return f'Number of files like {query} ' + str(total_file).zfill(3)

			result = str(total_file).zfill(3) + '\n'

			file_list = file_repository.get_files_with_copy_amount_by_querystring(conn, query)

			for file_row in file_list:
				file_md5 = file_row['file_md5']
				file_name = file_row['file_name']
				file_path = file_row['file_path']
				copies = file_row['copies']
				result = result + file_md5 + ' ' + file_name + ' ' + file_path + ' '+ str(copies).zfill(3) + '\n'
				peer_list = peer_repository.get_peers_by_file(conn, file_md5)
				for peer_row in peer_list:
					peer_session_id = peer_row['session_id']
					peer_ip = peer_row['ip']
					peer_name = peer_row['your_name']
					peer_port = peer_row['port']
					result = result + "---" + peer_session_id + ' ' +  peer_ip + ' ' + peer_name + ' ' + peer_port + "\n"
			conn.commit()
			conn.close()

		except database.Error as e:
			conn.rollback()
			conn.close()
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request.xxxxx"

		return f'Number of files like {query} ' + result

	elif command == "DREG":
		items = request.decode('utf-8')
		list_items = items.split('_')
		if len(list_items) != 3:
			return "Invalid request. Usage is: DREG_<file_md5>_<your_session_id>"
		
		session_id = list_items[2]
		md5 = list_items[1]

		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."
		try:
			peer = peer_repository.find(conn, session_id)

			if peer is None:
				conn.close()
				return "Unauthorized: your SessionID is invalid"

			file = file_repository.find(conn, md5)

			if file is None:
				return "File not found."

			file.download_count += 1
			file.update(conn)

			conn.commit()
			conn.close()

		except database.Error as e:
			conn.rollback()
			conn.close()
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		return f"ADRE register to download file md5 {md5} with name {file.file_name}." 

	elif command == "LOGO":
		items = request.decode('utf-8')
		list_items = items.split('_')
		if len(list_items) != 2:
			return "Invalid request. Usage is: LOGO_<your_session_id>"

		session_id = list_items[1]

		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row

		except database.Error as e:
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		try:
			peer = peer_repository.find(conn, session_id)

			if peer is None:
				conn.close()
				return "Unauthorized: your SessionID is invalid"

			deleted = file_repository.delete_peer_files(conn, session_id)

			peer.delete(conn)

			conn.commit()
			conn.close()

		except database.Error as e:
			conn.rollback()
			conn.close()
			print(f'Error: {e}')
			return "The server has encountered an error while trying to serve the request."

		return "ALGO" + str(deleted).zfill(3)
	elif command == "REGU":
		items = request.decode('utf-8')
		list_items = items.split('_')
		username = list_items[1]
		password = list_items[2]
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		peer_account = peer_repository.find_account(conn, username=username)
		if peer_account is not None:
			return "Error"
		else:
			session_id = str(uuid.uuid4().hex[:16].upper())
			peer = peer_repository.find(conn, session_id)
			while peer is not None:
				session_id = str(uuid.uuid4().hex[:16].upper())
				peer = peer_repository.find(conn, session_id)
			peer_account = Peer_account(session_id=session_id, username=username, password=password)
			peer_account.insert(conn=conn)
			conn.commit()
			return f"Successful_{session_id}"
	elif command == "SAPE":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		peer = Peer(session_id=list_items[1], ip = ip, your_name = list_items[2], port = list_items[3], state_on_off=list_items[4])
		peer.insert(conn=conn)
		conn.commit()
		conn.close()
		return "Successfull save peer"
	elif command == "LOGU":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		username = list_items[1]
		password = list_items[2]
		peer_account = peer_repository.find_account(conn=conn, username=username)
		if peer_account is not None:
			if password == peer_account.password_account:
				peer = peer_repository.find(conn, peer_account.session_id)
				peer.ip = ip
				peer.state_on_off = True
				peer.update(conn)
				conn.commit()
				return f"Successfull_{peer_account.session_id}"
			else:
				return "Error"
		else:
			return "Error"
		conn.close()
	elif command == "LOGX":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		username = list_items[1]
		password = list_items[2]
		peer_account = peer_repository.find_account(conn=conn, username=username)
		peer = peer_repository.find(conn, peer_account.session_id)
		peer.state_on_off = False
		peer.update(conn)
		conn.commit()
		conn.close()
		return "Successfull log out"
	elif command == "FINX":
		return find(request=request)
	elif command == "GELI":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		session_id = list_items[1]
		file_list = peer_repository.get_files_by_peer(conn=conn, session_id=session_id)
		conn.close()
		return file_list
	elif command == "GENA":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		session_id = list_items[1]
		username = peer_repository.find_account_by_session_id(conn=conn, session_id= session_id).username
		conn.close()
		return username
	elif command == "POIF":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		session_id = list_items[1]
		file_md5 = list_items[2]
		peer = peer_repository.find(conn=conn, session_id=session_id)
		filename = file_repository.find(conn=conn, file_md5=file_md5).file_name
		conn.close()
		print(peer.ip, peer.port, filename)
		return f"{peer.ip}_{peer.port}_{filename}"
	elif command == "POIP":
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		session_id = list_items[1]
		peer = peer_repository.find(conn=conn, session_id=session_id)
		conn.close()
		return f"{peer.ip}_{peer.port}"
	elif command == 'FIPA':
		try:
			conn = database.get_connection(db_file)
			conn.row_factory = database.sqlite3.Row
		except database.Error as e:
			print(f'Error: {e}')
		items = request.decode('utf-8')
		list_items = items.split('_')
		session_id = list_items[1]
		file_md5 = list_items[2]
		file_path = peer_repository.get_files_by_peer_and_file_ID(conn=conn, session_id=session_id, file_md5=file_md5)[0][2]
		return file_path
	else:
		return 'Command Error !!!'
	

def find(request: bytes):
	items = request.decode('utf-8')
	list_items = items.split('_')
	session_id = list_items[2]
	query = list_items[1]
	if query != '*':
		query = '%' + query + '%'
	try:
		conn = database.get_connection(db_file)
		conn.row_factory = database.sqlite3.Row

	except database.Error as e:
		print(f'Error: {e}')
		return "The server has encountered an error while trying to serve the request."

	try:
		peer = peer_repository.find(conn, session_id)

		if peer is None:
			conn.close()
			return "Unauthorized: your SessionID is invalid"

		total_file = file_repository.get_files_count_by_querystring(conn, query)
		if total_file == 0:
			return None

		result = str(total_file).zfill(3) + '\n'

		file_list = file_repository.get_files_with_copy_amount_by_querystring(conn, query)
		res_list = []
		for file_row in file_list:
			peer_list = peer_repository.get_peers_by_file(conn, file_row['file_md5'])
			for peer_row in peer_list:
				peer_ip = peer_row['ip']
				peer_name = peer_row['your_name']
				peer_port = peer_row['port']
				peer_state = peer_row['state_on_off']
				res_list.append({
					'file_name' : file_row['file_name'],
					'file_md5': file_row['file_md5'],
					'file_path': file_row['file_path'],
					'your_name': peer_name,
					'ip': peer_ip,
					'port': peer_port,
					'state_on_off': peer_state
				})

		conn.commit()
		conn.close()

	except database.Error as e:
		conn.rollback()
		conn.close()
		print(f'Error: {e}')
		return "The server has encountered an error while trying to serve the request."

	return res_list
