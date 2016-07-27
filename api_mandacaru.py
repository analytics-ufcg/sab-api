#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import unicodedata
from pyexcel_xlsx import get_data
from unicodedata import normalize
import IOFiles

def read_xlsx(file_name):
	file_data= get_data(file_name)
	return file_data


def info_reservatorios(id_reservatorio=None):
	dict_reserv = IOFiles.reservatorios()
	file_data = IOFiles.monitoramento()

	result_list =[]

	for d in dict_reserv["objects"]["reservatorios"]["geometries"]:
		if (id_reservatorio is None):
			result_list.append(d["properties"])
		else:
			if (d["properties"]["GEOCODIGO"] == id_reservatorio):
				return(json.dumps(d["properties"]))

	return(json.dumps(result_list))


def estados_br():
	return(json.dumps(IOFiles.estados_br()))

def estados_sab():
	return(json.dumps(IOFiles.estados_sab()))

def reservatorios():
	return(json.dumps(IOFiles.reservatorios()))



def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def remover_espacos(txt):
	return txt.replace(" ", "")