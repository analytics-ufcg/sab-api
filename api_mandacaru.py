#!/usr/bin/env python
# -*- coding: utf-8 -*-
import IO
import funcoes_aux
from dateutil import relativedelta
from datetime import datetime
import math

def states_sab():
	return(IO.states_sab())

def json_brazil():
	return(IO.json_brazil())

def reservoirs():
	query = ("SELECT mon.id,mon.latitude,mon.longitude, mon.capacidade, mo.volume_percentual, mo.volume"
		" FROM tb_monitoramento mo RIGHT JOIN "
		"(SELECT r.id,r.latitude,r.longitude, r.capacidade, max(m.data_informacao) AS maior_data "
		"FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon"
		" ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao AND mon.maior_data >= (CURDATE() - INTERVAL 90 DAY);")
	select_answer = IO.select_DB(query)

	keys = ["id", "latitude", "longitude", "capacidade","volume_percentual","volume"]

	features = []
	for line in select_answer:
		feature = {}
		geometry = {}
		properties = funcoes_aux.create_dictionary(line, keys)

		geometry["type"] = "Point"
		geometry["coordinates"] = [float(properties["longitude"]),float(properties["latitude"])]

		feature["geometry"] = geometry
		feature["type"] = "Feature"
		feature["properties"] = properties

		features.append(feature)

	answer = {}
	answer["type"] = "FeatureCollection"
	answer["features"] = features

	return answer

def reservoirs_information(res_id=None):
	if (res_id is None):
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
				" WHERE r.id="+str(res_id)+
				" GROUP BY r.id,mo.volume, mo.volume_percentual,aux.data_info")

	select_answer = IO.select_DB(query)

	keys = ["id","nome","perimetro","bacia","reservat","hectares","tipo","area","capacidade","volume","volume_percentual","data_informacao","municipio","estado"]

	return funcoes_aux.list_of_dictionarys(select_answer, keys, "info")

def reservoirs_monitoring(res_id,all_reservoirs=False):
	if(all_reservoirs):
		query = ("SELECT mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume FROM tb_monitoramento mo WHERE mo.id_reservatorio="+str(res_id)+
			" ORDER BY mo.data_informacao")
	else:
		query = ("SELECT mo.volume_percentual, date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume FROM tb_monitoramento mo WHERE mo.visualizacao=1 and mo.id_reservatorio="+str(res_id)+
			" ORDER BY mo.data_informacao")

	select_answer = IO.select_DB(query)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	volumes_list = []
	dates_list = []
	months_monitoring = monitoring_6_meses(res_id,all_reservoirs)
	date_final = datetime.strptime('31/12/1969', '%d/%m/%Y')

	for monitoring in months_monitoring:
		volumes_list.append(float(monitoring["Volume"]))
		date = datetime.strptime(monitoring["DataInformacao"], '%d/%m/%Y')
		if (date > date_final):
			date_final = date
		dates_list.append(float(date.strftime('%s')))

	inicial_date = date_final- relativedelta.relativedelta(months=6)

	regression_coefficient=0
	if(len(volumes_list)>0):
		regression_gradient = funcoes_aux.regression_gradient(volumes_list,dates_list)
		if(not math.isnan(regression_gradient)):
			regression_coefficient=regression_gradient

	data_monitoring = funcoes_aux.fix_data_interval_limit(select_answer)

	return {'volumes': funcoes_aux.list_of_dictionarys(data_monitoring, keys), 'volumes_recentes':{'volumes':months_monitoring, 
		'coeficiente_regressao': regression_coefficient, 'data_final':date_final.strftime('%d/%m/%Y'), 'data_inicial':inicial_date.strftime('%d/%m/%Y')}}


def monitoring_6_meses(res_id,all_reservoirs=False):
	if(all_reservoirs):
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(res_id)+
			" and data_informacao >= (CURDATE() - INTERVAL 6 MONTH) order by data_informacao;")
	else:
		query_min_graph = ("select volume_percentual, date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(res_id)+
			" and data_informacao >= (CURDATE() - INTERVAL 6 MONTH) order by data_informacao;")

	select_answer = IO.select_DB(query_min_graph)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	return funcoes_aux.list_of_dictionarys(select_answer,keys)


def reservoirs_similar(name, threshold):
	query = ("SELECT DISTINCT mon.id,mon.reservat,mon.nome, date_format(mon.maior_data,'%d/%m/%Y'), mo.volume_percentual, mo.volume, es.nome, es.sigla"
		" FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id,r.reservat,r.nome, max(m.data_informacao) AS maior_data"
		" FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon"
		" ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao LEFT JOIN tb_reservatorio_municipio re ON mon.id= re.id_reservatorio"
		" LEFT JOIN tb_municipio mu ON mu.id= re.id_municipio LEFT JOIN tb_estado es ON es.id= mu.id_estado;")
	select_answer = IO.select_DB(query)

	keys = ["id", "reservat","nome", "data", "volume_percentual","volume", "nome_estado", "uf"]

	reservoirs = funcoes_aux.list_of_dictionarys(select_answer, keys)

	similar = funcoes_aux.reservoirs_similar(name,reservoirs,threshold)

	return similar

def reservoirs_equivalent_hydrographic_basin():

	query = ("SELECT res.bacia AS bacia, ROUND(SUM(info.volume),2) AS volume_equivalente, ROUND(SUM(info.capacidade),2) AS capacidade_equivalente,"
		" ROUND((SUM(info.volume)/SUM(info.capacidade)*100),2) AS porcentagem_equivalente,"
		" COUNT(DISTINCT info.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT res.id)-COUNT(DISTINCT info.id_reservatorio)) AS quant_reservatorio_sem_info ,COUNT(DISTINCT res.id) AS total_reservatorios,"
		" COUNT(CASE WHEN info.volume_percentual <= 10 THEN 1 ELSE 0 END) AS intervalo_1,"
		" COUNT(CASE WHEN info.volume_percentual > 10 AND info.volume_percentual <=25 THEN 1 END) AS intervalo_2,"
		" COUNT(CASE WHEN info.volume_percentual > 25 AND info.volume_percentual <=50 THEN 1 END) AS intervalo_3,"
		" COUNT(CASE WHEN info.volume_percentual > 50 AND info.volume_percentual <=75 THEN 1 END) AS intervalo_4,"
		" COUNT(CASE WHEN info.volume_percentual > 75 THEN 1 END) AS intervalo_5"
		" FROM tb_reservatorio res LEFT JOIN (SELECT mo.volume AS volume, re.capacidade AS capacidade, re.id AS id_reservatorio,"
		" mo.volume_percentual AS volume_percentual"
		" FROM tb_monitoramento mo, tb_reservatorio re, (SELECT m.id_reservatorio as id_reserv, MAX(m.data_informacao) as data_info"
		" FROM tb_monitoramento m WHERE m.data_informacao >= (CURDATE() - INTERVAL 90 DAY) GROUP BY m.id_reservatorio) info_data"
		" WHERE info_data.id_reserv=mo.id_reservatorio AND re.id=mo.id_reservatorio AND mo.data_informacao=info_data.data_info) info"
		" ON info.id_reservatorio=res.id GROUP BY res.bacia;")

	select_answer = IO.select_DB(query)

	keys = ["bacia", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  "quant_reserv_intervalo_5"]

	return funcoes_aux.list_of_dictionarys(select_answer, keys)


def reservoirs_equivalent_states():
	query = ("SELECT estado_reservatorio.estado_nome AS estado,estado_reservatorio.estado_sigla AS sigla, ROUND(SUM(info.volume),2) AS volume_equivalente,"
		" ROUND(SUM(info.capacidade),2) AS capacidade_equivalente, ROUND((SUM(info.volume)/SUM(info.capacidade)*100),2) AS porcentagem_equivalente,"
		" COUNT(DISTINCT info.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT estado_reservatorio.id_reservatorio)-COUNT(DISTINCT info.id_reservatorio)) AS quant_reservatorio_sem_info,"
		" COUNT(DISTINCT estado_reservatorio.id_reservatorio) AS total_reservatorios,"
		" COUNT(CASE WHEN info.volume_percentual <= 10 THEN 1 END) AS intervalo_1,"
		" COUNT(CASE WHEN info.volume_percentual > 10 AND info.volume_percentual <=25 THEN 1 END) AS intervalo_2,"
		" COUNT(CASE WHEN info.volume_percentual > 25 AND info.volume_percentual <=50 THEN 1 END) AS intervalo_3,"
		" COUNT(CASE WHEN info.volume_percentual > 50 AND info.volume_percentual <=75 THEN 1 END) AS intervalo_4,"
		" COUNT(CASE WHEN info.volume_percentual > 75 THEN 1 END) AS intervalo_5"
		" FROM (SELECT DISTINCT mo.volume AS volume, re.capacidade AS capacidade, re.id AS id_reservatorio,"
		" mo.volume_percentual AS volume_percentual FROM tb_monitoramento mo, tb_reservatorio re,"
		" (SELECT m.id_reservatorio AS id_reserv, MAX(m.data_informacao) as data_info FROM tb_monitoramento m"
		" WHERE m.data_informacao >= (CURDATE() - INTERVAL 90 DAY) GROUP BY m.id_reservatorio) info_data"
		" WHERE info_data.id_reserv=mo.id_reservatorio AND re.id=mo.id_reservatorio AND mo.data_informacao=info_data.data_info) info"
		" RIGHT JOIN(select distinct res.id as id_reservatorio, es.nome as estado_nome, es.sigla as estado_sigla from tb_reservatorio res, tb_reservatorio_municipio rm,"
		" tb_municipio mu, tb_estado es where res.id=rm.id_reservatorio and mu.id=rm.id_municipio and mu.id_estado=es.id) estado_reservatorio"
		" ON estado_reservatorio.id_reservatorio=info.id_reservatorio GROUP BY estado_reservatorio.estado_nome, estado_reservatorio.estado_sigla;")

	select_answer = IO.select_DB(query)

	keys = ["estado", "uf", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  "quant_reserv_intervalo_5"]

	list_dictionarys = funcoes_aux.list_of_dictionarys(select_answer, keys)

	# Semiarido Brasileiro
	volume_equivalente = 0
	capacidade_equivalente = 0
	quant_reservatorio_com_info = 0
	quant_reservatorio_sem_info = 0
	total_reservatorios = 0
	quant_reserv_intervalo_1 = 0
	quant_reserv_intervalo_2 = 0
	quant_reserv_intervalo_3 = 0
	quant_reserv_intervalo_4 = 0
	quant_reserv_intervalo_5 = 0

	for i in range(len(list_dictionarys)):
		if(list_dictionarys[i]["uf"] == "AL"):
			list_dictionarys[i]["semiarido"] = "Semiárido Alagoano"
		elif(list_dictionarys[i]["uf"] == "PE"):
			list_dictionarys[i]["semiarido"] = "Semiárido Pernambucano"
		elif(list_dictionarys[i]["uf"] == "BA"):
			list_dictionarys[i]["semiarido"] = "Semiárido Baiano"
		elif(list_dictionarys[i]["uf"] == "PB"):
			list_dictionarys[i]["semiarido"] = "Semiárido Paraibano"
		elif(list_dictionarys[i]["uf"] == "CE"):
			list_dictionarys[i]["semiarido"] = "Semiárido Cearense"
		elif(list_dictionarys[i]["uf"] == "MG"):
			list_dictionarys[i]["semiarido"] = "Semiárido Mineiro"
		elif(list_dictionarys[i]["uf"] == "PI"):
			list_dictionarys[i]["semiarido"] = "Semiárido Piauiense"
		elif(list_dictionarys[i]["uf"] == "SE"):
			list_dictionarys[i]["semiarido"] = "Semiárido Sergipano"
		elif(list_dictionarys[i]["uf"] == "RN"):
			list_dictionarys[i]["semiarido"] = "Semiárido Potiguar"
		volume_equivalente = volume_equivalente + (list_dictionarys[i]["volume_equivalente"] if list_dictionarys[i]["volume_equivalente"] is not None else 0)
		capacidade_equivalente = capacidade_equivalente + (list_dictionarys[i]["capacidade_equivalente"] if list_dictionarys[i]["capacidade_equivalente"] is not None else 0)
		quant_reservatorio_com_info = quant_reservatorio_com_info + list_dictionarys[i]["quant_reservatorio_com_info"]
		quant_reservatorio_sem_info = quant_reservatorio_sem_info + list_dictionarys[i]["quant_reservatorio_sem_info"]
		total_reservatorios = total_reservatorios + list_dictionarys[i]["total_reservatorios"]
		quant_reserv_intervalo_1 = quant_reserv_intervalo_1 + list_dictionarys[i]["quant_reserv_intervalo_1"]
		quant_reserv_intervalo_2 = quant_reserv_intervalo_2 + list_dictionarys[i]["quant_reserv_intervalo_2"]
		quant_reserv_intervalo_3 = quant_reserv_intervalo_3 + list_dictionarys[i]["quant_reserv_intervalo_3"]
		quant_reserv_intervalo_4 = quant_reserv_intervalo_4 + list_dictionarys[i]["quant_reserv_intervalo_4"]
		quant_reserv_intervalo_5 = quant_reserv_intervalo_5 + list_dictionarys[i]["quant_reserv_intervalo_5"]


	list_dictionarys.append({"estado":"Semiarido", "uf":"Semiarido","semiarido":"Semiárido Brasileiro", "volume_equivalente":round(volume_equivalente,2),
		"capacidade_equivalente":round(capacidade_equivalente,2), "porcentagem_equivalente":round(volume_equivalente/capacidade_equivalente*100,2), 
		"quant_reservatorio_com_info":quant_reservatorio_com_info,"quant_reservatorio_sem_info":quant_reservatorio_sem_info,
		"total_reservatorios":total_reservatorios, "quant_reserv_intervalo_1":quant_reserv_intervalo_1, "quant_reserv_intervalo_2":quant_reserv_intervalo_2,
		 "quant_reserv_intervalo_3":quant_reserv_intervalo_3, "quant_reserv_intervalo_4":quant_reserv_intervalo_4, 
		 "quant_reserv_intervalo_5":quant_reserv_intervalo_5})

	return list_dictionarys