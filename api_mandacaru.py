#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import unicodedata
from pyexcel_xlsx import get_data
from unicodedata import normalize

def read_xlsx(file_name):
	file_data= get_data(file_name)
	return file_data


def info_reservatorios(id_reservatorio=None):
	dict_reserv = reservatorios_dicionario()
	file_data = monitoramento_xlsx()

	result_dict = {}

	for flap in file_data:
		lines = file_data[flap]
		list_dicts = []
		for i in range(1,len(lines)):
			internal_dict = {}
			if(len(lines[i]) > 0):
				try:
					for j in range(len(lines[i])):
						if (lines[i][0]==id_reservatorio or id_reservatorio is None):
							internal_dict[remover_espacos(remover_acentos(lines[0][j]))] = lines[i][j]
					extra_info = {}
					for d in dict_reserv["objects"]["reservatorios_geojson"]["geometries"]:
						if ((lines[i][0]==d["id"] and id_reservatorio is None) or d["id"]==id_reservatorio):
							extra_info["Tipo"] = d["properties"]["tipo"]
							extra_info["Estado"] = d["properties"]["estado"]
							extra_info["Finalidade"] = d["properties"]["finalidade"]
							extra_info["Hectares"] = d["properties"]["hectares"]
							extra_info["Perimetro"] = d["properties"]["perimetro"]
							break
				except Exception, e:
					print (lines[i])
					print(e)

			if (len(internal_dict)>0):
				internal_dict.update(extra_info)
				list_dicts.append(internal_dict)
		result_dict[remover_espacos(remover_acentos(flap))] = list_dicts

	if (id_reservatorio is None):
		return(json.dumps(result_dict["Reservatorio_ANA_JU"]))
	else:
		print(result_dict.keys())
		return(json.dumps(result_dict["Reservatorio_ANA_JU"][0]))


def estados_br():
	return(json.dumps(estados_br_dicionario()))

def estados_sab():
	return(json.dumps(estados_sab_dicionario()))

def reservatorios():
	return(json.dumps(reservatorios_dicionario()))


def reservatorios_dicionario():
	with open('data/reservatorios.json') as data_file:
		data = json.load(data_file)
	return data

def estados_sab_dicionario():
	with open('data/div_estadual_sab.json') as data_file:
		data = json.load(data_file)	
	return data

def estados_br_dicionario():
	with open('data/estado.json') as data_file:
		data = json.load(data_file)	
	return data

def monitoramento_xlsx():
	data = read_xlsx("data/moni_reserv_2016.xlsx")
	return data

def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def remover_espacos(txt):
	return txt.replace(" ", "")