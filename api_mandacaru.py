#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import unicodedata
from pyexcel_xlsx import get_data

def read_xlsx(file_name):
	file_data= get_data(file_name)
	return file_data


def monitoramento_todos_reservatorios():
	file_data = read_xlsx("data/moni_reserv_2016.xlsx")

	result_dict = {}

	for flap in file_data:
		lines = file_data[flap]
		list_dicts = []
		for i in range(1,len(lines)):
			internal_dict = {}
			for j in range(len(lines[i])):
				internal_dict[lines[0][j]] = lines[i][j]
			list_dicts.append(internal_dict)

		result_dict[flap] = list_dicts


	return(json.dumps(result_dict))


def regioes_brasil():
	with open('data/br.json') as data_file:
		data = json.load(data_file)
	return(json.dumps(data))


def cidades_sab():
	with open('data/sab.json') as data_file:
		data = json.load(data_file)
	return(json.dumps(data))

def reservatorios_sab():
	with open('data/reservatorios.json') as data_file:
		data = json.load(data_file)
	return(json.dumps(data))