#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import IO
import funcoes_aux

def estados_br():
	return(json.dumps(IO.estados_br()))

def estados_sab():
	return(json.dumps(IO.estados_sab()))

def reservatorios():
	query = ("SELECT r.id,r.capacidade FROM tb_reservatorio r")

	resposta_consulta = IO.consulta_BD(query)
	dict_capacidade = {}
	for r in resposta_consulta:
		dict_capacidade[r[0]] = r[1]

	reservatorios = IO.reservatorios()
	for reserv in reservatorios["objects"]["reservatorios"]["geometries"]:
		reserv["properties"]["CAPACIDADE"] = dict_capacidade[reserv["properties"]["ID"]]
	return(json.dumps(reservatorios))

# def municipios_sab():
# 	return(json.dumps(IO.municipios_sab()))


def info_reservatorios_BD(id_res=None):
	if (id_res is None):
		query = ("SELECT r.id,r.nome,r.perimetro,r.bacia,r.reservat,r.hectares"
				",r.tipo,r.area,r.capacidade"
				",mo.volume, mo.volume_percentual, date_format(aux.data_info,'%d/%m/%Y')"
				",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
				",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
				" FROM tb_reservatorio r JOIN tb_reservatorio_municipio rm ON r.id=rm.id_reservatorio"
				" JOIN tb_municipio m ON rm.id_municipio=m.id"
				" JOIN tb_estado e ON m.id_estado=e.id"
				" LEFT OUTER JOIN (select id_reservatorio as id_reserv, max(data_informacao) as data_info from tb_monitoramento group by id_reservatorio) aux"
				" ON aux.id_reserv=r.id"
				" LEFT OUTER JOIN tb_monitoramento mo ON (r.id=mo.id_reservatorio) and (mo.data_informacao=aux.data_info)"
				" GROUP BY r.id,mo.volume, mo.volume_percentual,aux.data_info")
	else:
		query = ("SELECT r.id,r.nome,r.perimetro,r.bacia,r.reservat,r.hectares"
				",r.tipo,r.area,r.capacidade"
				",mo.volume, mo.volume_percentual, date_format(aux.data_info,'%d/%m/%Y')"
				",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
				",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
				" FROM tb_reservatorio r JOIN tb_reservatorio_municipio rm ON r.id=rm.id_reservatorio"
				" JOIN tb_municipio m ON rm.id_municipio=m.id"
				" JOIN tb_estado e ON m.id_estado=e.id"
				" LEFT OUTER JOIN (select id_reservatorio as id_reserv, max(data_informacao) as data_info from tb_monitoramento group by id_reservatorio) aux"
				" ON aux.id_reserv=r.id"
				" LEFT OUTER JOIN tb_monitoramento mo ON (r.id=mo.id_reservatorio) and (mo.data_informacao=aux.data_info)"
				" WHERE r.id="+str(id_res)+
				" GROUP BY r.id,mo.volume, mo.volume_percentual,aux.data_info")

	resposta_consulta = IO.consulta_BD(query)

	keys = ["id","nome","perimetro","bacia","reservat","hectares","tipo","area","capacidade","volume","volume_percentual","data_informacao","municipio","estado"]

	return(json.dumps(funcoes_aux.lista_dicionarios(resposta_consulta, keys)))

def monitoramento_reservatorios_BD(id_reserv):
	query = ("SELECT mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume FROM tb_monitoramento mo WHERE mo.id_reservatorio="+str(id_reserv)+
		" ORDER BY mo.data_informacao desc")

	resposta_consulta = IO.consulta_BD(query)
	
	keys = ["VolumePercentual","DataInformacao", "Volume"]

	query_anos = ("SELECT YEAR(MAX(mo.data_informacao)), YEAR(MIN(mo.data_informacao)) FROM tb_monitoramento mo WHERE mo.id_reservatorio="+str(id_reserv))	
	resposta_consulta_anos = IO.consulta_BD_one(query_anos)

	keys_anos = ["ano_info_max","ano_info_min"]

	return(json.dumps({'volumes': funcoes_aux.lista_dicionarios(resposta_consulta, keys), 'anos':funcoes_aux.cria_dicionario(resposta_consulta_anos,keys_anos)}))
