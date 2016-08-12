#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unicodedata import normalize
import IO

def info_reservatorios(id_reservatorio=None):
	reservatorios_detalhes = IO.reservatorios_detalhes()

	if(id_reservatorio is None):
		return(json.dumps(reservatorios_detalhes))
	else:
		for reserv in reservatorios_detalhes:
			if (int(id_reservatorio) == int(reserv["GEOCODIGO"])):
				return(json.dumps(reserv))


def monitoramento_reservatorios(id):
	monitoramento = IO.monitoramento()
	try :
		return(json.dumps({'volumes': monitoramento[id]}))
	except :
		return(json.dumps({'volumes': []}))


def estados_br():
	return(json.dumps(IO.estados_br()))

def estados_sab():
	return(json.dumps(IO.estados_sab()))

def reservatorios():
	return(json.dumps(IO.reservatorios()))

def municipios_sab():
	return(json.dumps(IO.municipios_sab()))

def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def ajuste_acentos(txt):
	return unicode(txt, 'unicode-escape')

def remover_espacos(txt):
	return txt.replace(" ", "")


def info_reservatorios_BD(id_res=None):
	if (id_res is None):
		query = ("SELECT r.id,r.nome,r.perimetro,r.bacia,r.reservat,r.hectares"
				",r.tipo,r.area,r.capacidade"
				",mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y')"
				",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
				",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
				" FROM tb_reservatorio r, tb_municipio m, tb_reservatorio_municipio rm"
				", tb_estado e, tb_monitoramento mo, "
				"(select id_reservatorio as id_reserv, max(data_informacao) as data_info from tb_monitoramento group by id_reservatorio) aux"
				" WHERE rm.id_municipio= m.id and r.id=rm.id_reservatorio"
				" and e.id=m.id_estado and mo.id_reservatorio=r.id and mo.data_informacao=aux.data_info and aux.id_reserv=mo.id_reservatorio"
				" GROUP BY r.id,mo.volume, mo.volume_percentual")
	else:
				query = ("SELECT r.id,r.nome,r.perimetro,r.bacia,r.reservat,r.hectares"
				",r.tipo,r.area,r.capacidade"
				",mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y')"
				",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
				",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
				" FROM tb_reservatorio r, tb_municipio m, tb_reservatorio_municipio rm"
				", tb_estado e, tb_monitoramento mo, "
				"(select id_reservatorio as id_reserv, max(data_informacao) as data_info from tb_monitoramento group by id_reservatorio) aux"
				" WHERE rm.id_municipio= m.id and r.id=rm.id_reservatorio and r.id="+str(id_res)+
				" and e.id=m.id_estado and mo.id_reservatorio=r.id and mo.data_informacao=aux.data_info and aux.id_reserv=mo.id_reservatorio"
				" GROUP BY r.id,mo.volume, mo.volume_percentual")

	resposta_consulta = IO.consulta_BD(query)

	keys = ["id","nome","perimetro","bacia","reservat","hectares","tipo","area","capacidade","volume","volume_percentual","data_informacao","municipio","estado"]
	#print lista_dicionarios(resposta_consulta, keys)
	return(json.dumps(lista_dicionarios(resposta_consulta, keys)))

def lista_dicionarios(list_of_values, keys):
	lista_resposta = []
	for valor in list_of_values:
		lista_resposta.append(cria_dicionario(valor,keys))
	return lista_resposta

def cria_dicionario(values, keys):
	dicionario = {}
	for i in range(len(keys)):
		if (type(values[i]) is str):
			dicionario[keys[i]] = ajuste_acentos(values[i])
		else:
			dicionario[keys[i]] = values[i]
	return dicionario