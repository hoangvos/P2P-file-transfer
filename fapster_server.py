#!/usr/bin/env python

from service.Server import Server
from database import database
from utils import shell_colors as shell

if __name__ == '__main__':
	DB_FILE = 'directory.db'

	if not database.exist(DB_FILE):
		database.create_database(DB_FILE)
	else:
		database.reset_database(DB_FILE)

	Server(3000).run()

