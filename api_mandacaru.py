#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import json
import unicodedata
from pyexcel_xlsx import get_data

def read_xlsx(file_name):
	file_data= get_data(file_name)
	return file_data


def info_reservatorios(id_reservatorio=None):
	dict_reserv = reservatorios_sab_dicionario()
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
							internal_dict[lines[0][j]] = lines[i][j]
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
		result_dict[flap] = list_dicts

	return(json.dumps(result_dict))


def regioes_brasil():
	return(json.dumps(regioes_sab_dicionario()))

def estados_brasil():
	return(json.dumps(estados_sab_dicionario()))


def cidades_sab():
	return(json.dumps(cidades_sab_dicionario()))

def limites_sab():
	return(json.dumps(limites_sab_dicionario()))

def div_estadual_sab():
	return(json.dumps(div_estadual_sab_dicionario()))

def reservatorios_sab():
	return(json.dumps(reservatorios_sab_dicionario()))


def reservatorios_sab_dicionario():
	with open('data/reservatorios.json') as data_file:
		data = json.load(data_file)
	return data

def cidades_sab_dicionario():
	with open('data/sab.json') as data_file:
		data = json.load(data_file)	
	return data

def limites_sab_dicionario():
	with open('data/limite.json') as data_file:
		data = json.load(data_file)	
	return data

def div_estadual_sab_dicionario():
	with open('data/div_estadual_sab.json') as data_file:
		data = json.load(data_file)	
	return data

def regioes_sab_dicionario():
	with open('data/br.json') as data_file:
		data = json.load(data_file)	
	return data

def estados_sab_dicionario():
	with open('data/estado.json') as data_file:
		data = json.load(data_file)	
	return data

def monitoramento_xlsx():
	data = read_xlsx("data/moni_reserv_2016.xlsx")
	return data