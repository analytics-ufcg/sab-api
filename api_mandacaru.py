#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
from unicodedata import normalize
import IOFiles

def info_reservatorios(id_reservatorio=None):
	dict_reserv = IOFiles.reservatorios()

	result_list =[]

	for d in dict_reserv["objects"]["reservatorios"]["geometries"]:
		if (id_reservatorio is None):
			result_list.append(d["properties"])
		else:
			if (d["properties"]["GEOCODIGO"] == id_reservatorio):
				return(json.dumps(d["properties"]))

	return(json.dumps(result_list))


def monitoramento_reservatorios(id):
	monitoramento = IOFiles.monitoramento()
	return(json.dumps(monitoramento[id]))


def estados_br():
	return(json.dumps(IOFiles.estados_br()))

def estados_sab():
	return(json.dumps(IOFiles.estados_sab()))

def reservatorios():
	return(json.dumps(IOFiles.reservatorios()))

def municipios_sab():
	return(json.dumps(IOFiles.municipios_sab()))

def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def remover_espacos(txt):
	return txt.replace(" ", "")