#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import os
import MySQLdb


path_local = os.path.dirname(os.path.realpath(__file__))


with open(path_local+'/data/div_estadual.json') as data_file:
	_state_division_sab = json.load(data_file)	

def states_sab():
	"""return a json"""
	return _state_division_sab

def select_DB(query):
	""" Connect to MySQL database """
	try:
		conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
		cursor = conn.cursor()

		cursor.execute(query)

		rows = cursor.fetchall()

	finally:
		cursor.close()
		conn.close()
	
	return rows
 
def select_one_DB(query):
	""" Connect to MySQL database """
	try:
		conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
		cursor = conn.cursor()

		cursor.execute(query)

		rows = cursor.fetchone()

	finally:
		cursor.close()
		conn.close()
	
	return rows
 