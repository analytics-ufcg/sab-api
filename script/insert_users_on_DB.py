#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from unicodedata import normalize
import aux_collection_insert
from hashlib import md5

def hash_all(*args):
    strings = map(str, args)
    hashed = md5(':'.join(strings))
    return hashed.hexdigest()

def drop_table():
	query = '''DROP TABLE IF EXISTS tb_user'''
	aux_collection_insert.update_BD(query)

def create_table():
	query = '''CREATE TABLE IF NOT EXISTS tb_user (
	id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, 
	username VARCHAR(45) NOT NULL, 
	password VARCHAR(60) NOT NULL)'''
	aux_collection_insert.update_BD(query)
	
def insert_user(username, password):
	hashed_pass = hash_all(username, 'INSA', password)	
	query = '''INSERT INTO tb_user (username, password) 
	VALUES ("''' + username + '''","''' + hashed_pass + '''")'''
	aux_collection_insert.update_BD(query)

drop_table()	
create_table()
insert_user('insa', 'volup14')
insert_user('igor', '12345')
