#!/usr/bin/env python
# -*- coding: utf-8 -*-
import IO
import funcoes_aux
from dateutil import relativedelta
from datetime import datetime
import math

def estados_sab():
	return(IO.estados_sab())

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

	return(resposta)

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

	return(funcoes_aux.lista_dicionarios(resposta_consulta, keys, "info"))

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
		grad_regressao = funcoes_aux.gradiente_regressao(lista_volumes,lista_datas)
		if(not math.isnan(grad_regressao)):
			coeficiente_regressao=grad_regressao

	monitoramento_dados = funcoes_aux.ajuste_dados_com_intervalo(resposta_consulta)

	return({'volumes': funcoes_aux.lista_dicionarios(monitoramento_dados, keys), 'volumes_recentes':{'volumes':monitoramento_meses, 
		'coeficiente_regressao': coeficiente_regressao, 'data_final':data_final.strftime('%d/%m/%Y'), 'data_inicial':data_inicial.strftime('%d/%m/%Y')}})


def monitoramento_6meses(id_reserv,completo=False):
	if(completo):
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(id_reserv)+
			" and data_informacao >= (CURDATE() - INTERVAL 6 MONTH) order by data_informacao;")
	else:
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(id_reserv)+
			" and data_informacao >= (CURDATE() - INTERVAL 6 MONTH) order by data_informacao;")

	resposta_consulta_min_graph = IO.consulta_BD(query_min_graph)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	return funcoes_aux.lista_dicionarios(resposta_consulta_min_graph,keys)


def similares_reservatorios(nome):
	query = ("SELECT DISTINCT mon.id,mon.reservat,mon.nome, date_format(mon.maior_data,'%d/%m/%Y'), mo.volume_percentual, mo.volume, es.nome, es.sigla"
		" FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id,r.reservat,r.nome, max(m.data_informacao) AS maior_data"
		" FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon"
		" ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao LEFT JOIN tb_reservatorio_municipio re ON mon.id= re.id_reservatorio"
		" LEFT JOIN tb_municipio mu ON mu.id= re.id_municipio LEFT JOIN tb_estado es ON es.id= mu.id_estado;")
	resposta_consulta = IO.consulta_BD(query)

	keys = ["id", "reservat","nome", "data", "volume_percentual","volume", "nome_estado", "uf"]

	reservatorios = funcoes_aux.lista_dicionarios(resposta_consulta, keys)

	similares = funcoes_aux.reservatorios_similares(nome,reservatorios)

	return(similares)

def reservatorio_equivalente_bacia():

	query = ("SELECT res.bacia AS bacia, ROUND(SUM(info.volume),2) AS volume_equivalente, ROUND(SUM(info.capacidade),2) AS capacidade_equivalente,"
		" ROUND((SUM(info.volume)/SUM(info.capacidade)*100),2) AS porcentagem_equivalente,"
		" COUNT(DISTINCT info.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT res.id)-COUNT(DISTINCT info.id_reservatorio)) AS quant_reservatorio_sem_info ,COUNT(DISTINCT res.id) AS total_reservatorios,"
		" CAST(SUM(CASE WHEN info.volume_percentual <= 10 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_1,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 10 AND info.volume_percentual <=25 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_2,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 25 AND info.volume_percentual <=50 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_3,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 50 AND info.volume_percentual <=75 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_4,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 75 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_5"
		" FROM tb_reservatorio res LEFT JOIN (SELECT mo.volume AS volume, re.capacidade AS capacidade, re.id AS id_reservatorio,"
		" mo.volume_percentual AS volume_percentual"
		" FROM tb_monitoramento mo, tb_reservatorio re, (SELECT m.id_reservatorio as id_reserv, MAX(m.data_informacao) as data_info"
		" FROM tb_monitoramento m WHERE m.data_informacao >= (CURDATE() - INTERVAL 90 DAY) GROUP BY m.id_reservatorio) info_data"
		" WHERE info_data.id_reserv=mo.id_reservatorio AND re.id=mo.id_reservatorio AND mo.data_informacao=info_data.data_info) info"
		" ON info.id_reservatorio=res.id GROUP BY res.bacia;")

	resposta_consulta = IO.consulta_BD(query)

	keys = ["bacia", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_5",
	  "quant_reserv_intervalo_5"]

	return(funcoes_aux.lista_dicionarios(resposta_consulta, keys))


def reservatorio_equivalente_estado():
	query = ("SELECT es.nome AS estado, ROUND(SUM(info.volume),2) AS volume_equivalente, ROUND(SUM(info.capacidade),2) AS capacidade_equivalente,"
		" ROUND((SUM(info.volume)/SUM(info.capacidade)*100),2) AS porcentagem_equivalente, COUNT(DISTINCT info.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT res.id)-COUNT(DISTINCT info.id_reservatorio)) AS quant_reservatorio_sem_info ,COUNT(DISTINCT res.id) AS total_reservatorios,"
		" CAST(SUM(CASE WHEN info.volume_percentual <= 10 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_1,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 10 AND info.volume_percentual <=25 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_2,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 25 AND info.volume_percentual <=50 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_3,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 50 AND info.volume_percentual <=75 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_4,"
		" CAST(SUM(CASE WHEN info.volume_percentual > 75 THEN 1 ELSE 0 END) as UNSIGNED) AS intervalo_5"
		" FROM tb_reservatorio res LEFT JOIN (SELECT mo.volume AS volume, re.capacidade AS capacidade, re.id AS id_reservatorio,"
		" mo.volume_percentual AS volume_percentual FROM tb_monitoramento mo, tb_reservatorio re,"
		" (SELECT m.id_reservatorio AS id_reserv, MAX(m.data_informacao) as data_info FROM tb_monitoramento m"
		" WHERE m.data_informacao >= (CURDATE() - INTERVAL 90 DAY) GROUP BY m.id_reservatorio) info_data"
		" WHERE info_data.id_reserv=mo.id_reservatorio AND re.id=mo.id_reservatorio AND mo.data_informacao=info_data.data_info) info"
		" ON info.id_reservatorio=res.id INNER JOIN tb_reservatorio_municipio rm ON rm.id_reservatorio=res.id INNER JOIN tb_municipio mu"
		" ON rm.id_municipio=mu.id INNER JOIN tb_estado es ON es.id=mu.id_estado GROUP BY es.nome;")

	resposta_consulta = IO.consulta_BD(query)

	keys = ["estado", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_5",
	  "quant_reserv_intervalo_5"]

	return(funcoes_aux.lista_dicionarios(resposta_consulta, keys))