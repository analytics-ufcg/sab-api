#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import unicodedata
import copy
from pyexcel_xlsx import get_data
from unicodedata import normalize

with open('data/reservatorios.json') as data_file:
	_reservatorios = json.load(data_file)

with open('data/div_estadual_sab.json') as data_file:
	_div_estadual_sab = json.load(data_file)	

with open('data/estado.json') as data_file:
	_estados_br = json.load(data_file)	

_monitoramento = get_data("data/moni_reserv_2016.xlsx")


def reservatorios():
	"""return a dictionary"""
	return _reservatorios

def estados_sab():
	"""return a dictionary"""
	return _div_estadual_sab

def estados_br():
	"""return a dictionary"""
	return _estados_br

def monitoramento():
	"""return a dictionary"""
	return _monitoramento
