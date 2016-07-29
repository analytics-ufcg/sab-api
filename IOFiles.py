#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import csv
from pyexcel_xlsx import get_data
from unicodedata import normalize

with open('data/reservatorios.json') as data_file:
	_reservatorios = json.load(data_file)

with open('data/div_estadual_sab.json') as data_file:
	_div_estadual_sab = json.load(data_file)	

with open('data/estados_br.json') as data_file:
	_estados_br = json.load(data_file)

with open('data/municipios_sab.json') as data_file:
	_municipios_sab = json.load(data_file)


_reservatorios_detalhes = []
with open('data/reservatorios.csv', 'rb') as csvfile:
	spamreader = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))
	for numeroLinha in range(1,len(spamreader)):
		_dicionario_interno = {}
		for numeroColuna in range(0,len(spamreader[numeroLinha])):
			_dicionario_interno[spamreader[0][numeroColuna]] = spamreader[numeroLinha][numeroColuna]
		_reservatorios_detalhes.append(_dicionario_interno)



_monitoramento = {}
with open('data/reservatoriosTotal.csv', 'rb') as csvfile:
	spamreader = list(list(rec) for rec in csv.reader(csvfile, delimiter=','))

	for numeroLinha in range(1,len(spamreader)):
		if (int(spamreader[numeroLinha][0]) not in _monitoramento):
			_monitoramento[int(spamreader[numeroLinha][0])] = []
		_dicionario_interno = {}
		for numeroColuna in range(0,len(spamreader[numeroLinha])):
			_dicionario_interno[spamreader[0][numeroColuna]] = spamreader[numeroLinha][numeroColuna]
		_monitoramento[int(spamreader[numeroLinha][0])].append(_dicionario_interno)

def reservatorios():
	"""return a dictionary"""
	return _reservatorios

def reservatorios_detalhes():
	"""return a list"""
	return _reservatorios_detalhes

def municipios_sab():
	"""return a dictionary"""
	return _municipios_sab

def estados_sab():
	"""return a dictionary"""
	return _div_estadual_sab

def estados_br():
	"""return a dictionary"""
	return _estados_br

def monitoramento():
	"""return a dictionary"""
	return _monitoramento
