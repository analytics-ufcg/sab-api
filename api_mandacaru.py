#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import IO
import funcoes_aux
from scipy import stats
from dateutil import relativedelta
from datetime import datetime
import math

# def estados_br():
# 	return(json.dumps(IO.estados_br()))

def estados_sab():
	return(json.dumps(IO.estados_sab()))

def reservatorios():
	query = ("SELECT mon.id,mon.latitude,mon.longitude, mon.capacidade, mo.volume_percentual, mo.volume"
		" FROM tb_monitoramento mo RIGHT JOIN "
		"(SELECT r.id,r.latitude,r.longitude, r.capacidade, max(m.data_informacao) AS maior_data "
		"FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon"
		" ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao;")
	resposta_consulta = IO.consulta_BD(query)

	keys = ["id", "latitude", "longitude", "capacidade","volume_percentual","volume"]

	features = []
	for linha in resposta_consulta:
		feature = {}
		geometry = {}
		propriedades = funcoes_aux.cria_dicionario(linha, keys)

		geometry["type"] = "Point"
		geometry["coordinates"] = [float(propriedades["longitude"]),float(propriedades["latitude"])]

		feature["geometry"] = geometry
		feature["type"] = "Feature"
		feature["properties"] = propriedades

		features.append(feature)

	resposta = {}
	resposta["type"] = "FeatureCollection"
	resposta["features"] = features

	return(json.dumps(resposta))

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

def monitoramento_reservatorios_BD(id_reserv,completo=False):
	if(completo):
		query = ("SELECT mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume FROM tb_monitoramento mo WHERE mo.id_reservatorio="+str(id_reserv)+
			" ORDER BY mo.data_informacao")
	else:
		query = ("SELECT mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume FROM tb_monitoramento mo WHERE mo.visualizacao=1 and mo.id_reservatorio="+str(id_reserv)+
			" ORDER BY mo.data_informacao")

	resposta_consulta = IO.consulta_BD(query)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	lista_volumes = []
	lista_datas = []
	monitoramento_meses = monitoramento_6meses(id_reserv,completo)
	data_final = datetime.strptime('31/12/1969', '%d/%m/%Y')

	for monitoramento in monitoramento_meses:
		lista_volumes.append(float(monitoramento["Volume"]))
		data = datetime.strptime(monitoramento["DataInformacao"], '%d/%m/%Y')
		if (data > data_final):
			data_final = data
		lista_datas.append(float(data.strftime('%s')))

	data_inicial = data_final- relativedelta.relativedelta(months=6)

	coeficiente_regressao=0
	if(len(lista_volumes)>0):
		grad_regressao = gradiente_regressao(lista_volumes,lista_datas)
		if(not math.isnan(grad_regressao)):
			coeficiente_regressao=grad_regressao

	monitoramento_dados = funcoes_aux.ajuste_dados_com_intervalo(resposta_consulta)

	return(json.dumps({'volumes': funcoes_aux.lista_dicionarios(monitoramento_dados, keys),
		'volumes_recentes':{'volumes':monitoramento_meses, 'coeficiente_regressao': coeficiente_regressao, 'data_final':data_final.strftime('%d/%m/%Y')
		, 'data_inicial':data_inicial.strftime('%d/%m/%Y')}}))


def gradiente_regressao(lista1,lista2):
	gradient, intercept, r_value, p_value, std_err = stats.linregress(lista1,lista2)
	return gradient

def monitoramento_6meses(id_reserv,completo=False):
	if(completo):
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(id_reserv)+
			" and data_informacao BETWEEN ((select max(data_informacao) from tb_monitoramento where id_reservatorio="+str(id_reserv)+
			")  - INTERVAL 6 MONTH) AND (select max(data_informacao) from tb_monitoramento where id_reservatorio="+str(id_reserv)+") order by data_informacao;")
	else:
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(id_reserv)+
			" and data_informacao BETWEEN ((select max(data_informacao) from tb_monitoramento where visualizacao=1 and id_reservatorio="+str(id_reserv)+
			")  - INTERVAL 6 MONTH) AND (select max(data_informacao) from tb_monitoramento where id_reservatorio="+str(id_reserv)+") order by data_informacao;")

	resposta_consulta_min_graph = IO.consulta_BD(query_min_graph)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	return funcoes_aux.lista_dicionarios(resposta_consulta_min_graph,keys)
