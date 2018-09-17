#!/usr/bin/env python
# -*- coding: utf-8 -*-
import IO
import funcoes_aux
from dateutil import relativedelta
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from flask import abort
import math
import StringIO
import csv
import re

ALLOWED_EXTENSIONS = set(['csv'])

def states_sab():
	return(IO.states_sab())

def json_brazil():
	return(IO.json_brazil())

def reservoirs():
	query = ("SELECT id_reservatorio, latitude, longitude, capacidade, "
		"IF(data_informacao  >= (CURDATE() - INTERVAL 90 DAY), volume_percentual, null) as volume_percentual,"
		"IF(data_informacao  >= (CURDATE() - INTERVAL 90 DAY), volume, null) as volume,"
		"IF(data_informacao  >= (CURDATE() - INTERVAL 90 DAY), date_format(data_informacao,'%d/%m/%Y'), null) as data_informacao, fonte"
		" from mv_monitoramento;")
	select_answer = IO.select_DB(query)

	keys = ["id", "latitude", "longitude", "capacidade","volume_percentual","volume", "data_informacao", "fonte"]

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
		    ",r.tipo,r.area,r.capacidade,mv_mo.fonte"
		    ",mv_mo.volume, ROUND(mv_mo.volume_percentual,1), date_format(mv_mo.data_informacao,'%d/%m/%Y')"
		    ",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
		    ",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
		    ",GROUP_CONCAT(DISTINCT e.sigla SEPARATOR ' / ') uf"
		    ",curso_barrado, cota_soleira, evaporacao_representativa, localizacao, posto_pluviometrico, area_bacia_nao_controlada, unidade_planejamento "
		    " FROM tb_reservatorio r JOIN tb_reservatorio_municipio rm ON r.id=rm.id_reservatorio"
		    " JOIN tb_municipio m ON rm.id_municipio=m.id"
		    " JOIN tb_estado e ON m.id_estado=e.id"
		    " LEFT OUTER JOIN mv_monitoramento mv_mo"
		    " ON mv_mo.id_reservatorio=r.id"
		    " LEFT JOIN tb_reservatorio_info info"
		    " ON info.id_reservatorio =r.id"
		    " GROUP BY r.id,mv_mo.volume, mv_mo.volume_percentual,mv_mo.data_informacao")
	else:
		query = ("SELECT r.id,r.nome,r.perimetro,r.bacia,r.reservat,r.hectares"
				",r.tipo,r.area,r.capacidade,mv_mo.fonte"
				",mv_mo.volume, ROUND(mv_mo.volume_percentual,1), date_format(mv_mo.data_informacao,'%d/%m/%Y')"
				",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
				",GROUP_CONCAT(DISTINCT e.nome SEPARATOR ' / ') estado"
				",GROUP_CONCAT(DISTINCT e.sigla SEPARATOR ' / ') uf"
				", curso_barrado, cota_soleira, evaporacao_representativa, localizacao, posto_pluviometrico, area_bacia_nao_controlada, unidade_planejamento"
				" FROM tb_reservatorio r JOIN tb_reservatorio_municipio rm ON r.id=rm.id_reservatorio AND r.id="+str(res_id)+
				" JOIN tb_municipio m ON rm.id_municipio=m.id"
				" JOIN tb_estado e ON m.id_estado=e.id"
				" LEFT OUTER JOIN mv_monitoramento mv_mo"
				" ON mv_mo.id_reservatorio=r.id"
				" LEFT JOIN tb_reservatorio_info info"
				" ON info.id_reservatorio =r.id"
				" GROUP BY r.id,mv_mo.volume, mv_mo.volume_percentual,mv_mo.data_informacao")

	select_answer = IO.select_DB(query)
	keys = ["id","nome","perimetro","bacia","reservat","hectares","tipo","area","capacidade","fonte","volume","volume_percentual","data_informacao","municipio","estado", "uf", "curso_barrado", "cota_soleira", "evaporacao_representativa", "localizacao", "posto_pluviometrico", "area_bacia_nao_controlada", "unidade_planejamento"]

	return funcoes_aux.list_of_dictionarys(select_answer, keys, "info")

def reservoirs_monitoring(res_id,all_monitoring=False):
	if(all_monitoring):
		query = ("SELECT ROUND(mo.volume_percentual,1), date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume, mo.fonte FROM tb_monitoramento mo WHERE mo.id_reservatorio="+str(res_id)+
			" ORDER BY mo.data_informacao")
	else:
		query = ("SELECT ROUND(mo.volume_percentual,1), date_format(mo.data_informacao,'%d/%m/%Y'), mo.volume, mo.fonte FROM tb_monitoramento mo WHERE mo.visualizacao=1 and mo.id_reservatorio="+str(res_id)+
			" ORDER BY mo.data_informacao")

	select_answer = IO.select_DB(query)

	keys = ["VolumePercentual","DataInformacao", "Volume","Fonte"]

	volumes_list = []
	dates_list = []
	months_monitoring = monitoring_months(res_id,6)
	last_month_monitoring = monitoring_months(res_id,1)
	date_final = datetime.strptime('31/12/1969', '%d/%m/%Y')

	for monitoring in last_month_monitoring:
		volumes_list.append(float(monitoring["Volume"]))
		date = datetime.strptime(monitoring["DataInformacao"], '%d/%m/%Y')
		if (date > date_final):
			date_final = date
		dates_list.append(float(date.strftime('%s')))

	inicial_date = date_final - relativedelta.relativedelta(months=6)

	regression_coefficient=0
	if(len(volumes_list)>0):
		regression_gradient = funcoes_aux.regression_gradient(volumes_list,dates_list)
		if(not math.isnan(regression_gradient)):
			regression_coefficient=regression_gradient

	data_monitoring = funcoes_aux.fix_data_interval_limit(select_answer)

	return {'volumes': funcoes_aux.list_of_dictionarys(data_monitoring, keys), 'volumes_recentes':{'volumes':months_monitoring,
		'coeficiente_regressao': regression_coefficient, 'data_final':date_final.strftime('%d/%m/%Y'), 'data_inicial':inicial_date.strftime('%d/%m/%Y')}}

def reservoirs_monitoring_csv(res_id):
	monitoring_json = reservoirs_monitoring(res_id,True)
	volumes = monitoring_json["volumes"]
	saida = [['Volume','VolumePercentual','Fonte','DataInformacao']]
	for volume in volumes:
		if 'Fonte' in volume:
			saida.append(volume.values())
	return saida


def monitoring_months(res_id,months):
	query_min_graph = ("select ROUND(volume_percentual,1), date_format(data_informacao,'%d/%m/%Y'), volume from tb_monitoramento where id_reservatorio ="+str(res_id)+
			" and visualizacao = 1 and data_informacao >= (CURDATE() - INTERVAL " + str(months) + " MONTH) order by data_informacao;")

	select_answer = IO.select_DB(query_min_graph)

	keys = ["VolumePercentual","DataInformacao", "Volume"]

	return funcoes_aux.list_of_dictionarys(select_answer,keys)


def reservoirs_similar(name, threshold):
	query = ("SELECT DISTINCT r.id,r.reservat,r.nome, date_format(mv_mo.data_informacao,'%d/%m/%Y'), ROUND(mv_mo.volume_percentual,1), mv_mo.volume, es.nome, es.sigla"
		" FROM mv_monitoramento mv_mo RIGHT JOIN tb_reservatorio r"
		" ON mv_mo.id_reservatorio=r.id LEFT JOIN tb_reservatorio_municipio re ON mv_mo.id_reservatorio= re.id_reservatorio"
		" LEFT JOIN tb_municipio mu ON mu.id= re.id_municipio LEFT JOIN tb_estado es ON es.id= mu.id_estado;")
	select_answer = IO.select_DB(query)

	keys = ["id", "reservat","nome", "data", "volume_percentual","volume", "nome_estado", "uf"]

	reservoirs = funcoes_aux.list_of_dictionarys(select_answer, keys)

	similar = funcoes_aux.reservoirs_similar(name,reservoirs,threshold)

	return similar

def reservoirs_equivalent_hydrographic_basin():
	query = ("SELECT res.bacia AS bacia, ROUND(SUM(mv_mo.volume),2) AS volume_equivalente, ROUND(SUM(mv_mo.capacidade),2) AS capacidade_equivalente,"
		" ROUND((SUM(mv_mo.volume)/SUM(mv_mo.capacidade)*100),1) AS porcentagem_equivalente,"
		" COUNT(DISTINCT mv_mo.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT res.id)-COUNT(DISTINCT mv_mo.id_reservatorio)) AS quant_reservatorio_sem_info ,COUNT(DISTINCT res.id) AS total_reservatorios,"
		" COUNT(CASE WHEN mv_mo.volume_percentual <= 10 THEN 1 ELSE 0 END) AS intervalo_1,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 10 AND mv_mo.volume_percentual <=25 THEN 1 END) AS intervalo_2,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 25 AND mv_mo.volume_percentual <=50 THEN 1 END) AS intervalo_3,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 50 AND mv_mo.volume_percentual <=75 THEN 1 END) AS intervalo_4,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 75 THEN 1 END) AS intervalo_5"
		" FROM tb_reservatorio res LEFT JOIN mv_monitoramento mv_mo"
		" ON mv_mo.data_informacao  >= (CURDATE() - INTERVAL 90 DAY) AND mv_mo.id_reservatorio=res.id GROUP BY res.bacia;")

	select_answer = IO.select_DB(query)

	keys = ["bacia", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  "quant_reserv_intervalo_5"]

	return funcoes_aux.list_of_dictionarys(select_answer, keys)


def reservoirs_equivalent_states(upper=0, lower=90):
	query = ("SELECT estado_reservatorio.estado_nome AS estado, estado_reservatorio.estado_sigla AS sigla, ROUND(SUM(mv_mo.volume),2) AS volume_equivalente,"
		" ROUND(SUM(mv_mo.capacidade),2) AS capacidade_equivalente, ROUND((SUM(mv_mo.volume)/SUM(mv_mo.capacidade)*100),1) AS porcentagem_equivalente,"
		" COUNT(DISTINCT mv_mo.id_reservatorio) AS quant_reservatorio_com_info,"
		" (COUNT(DISTINCT estado_reservatorio.id_reservatorio)-COUNT(DISTINCT mv_mo.id_reservatorio)) AS quant_reservatorio_sem_info,"
		" COUNT(DISTINCT estado_reservatorio.id_reservatorio) AS total_reservatorios,"
		" COUNT(CASE WHEN mv_mo.volume_percentual <= 10 THEN 1 END) AS intervalo_1,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 10 AND mv_mo.volume_percentual <=25 THEN 1 END) AS intervalo_2,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 25 AND mv_mo.volume_percentual <=50 THEN 1 END) AS intervalo_3,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 50 AND mv_mo.volume_percentual <=75 THEN 1 END) AS intervalo_4,"
		" COUNT(CASE WHEN mv_mo.volume_percentual > 75 THEN 1 END) AS intervalo_5"
		" FROM mv_monitoramento mv_mo RIGHT JOIN (select distinct res.id as id_reservatorio, es.nome as estado_nome, es.sigla as estado_sigla"
		" FROM tb_reservatorio res, tb_reservatorio_municipio rm, tb_municipio mu, tb_estado es"
		" WHERE res.id=rm.id_reservatorio and mu.id=rm.id_municipio and mu.id_estado=es.id) estado_reservatorio"
		" ON estado_reservatorio.id_reservatorio=mv_mo.id_reservatorio AND (CURDATE() - INTERVAL "+str(upper)+ " DAY) >= mv_mo.data_informacao AND mv_mo.data_informacao >= (CURDATE() - INTERVAL "+str(lower)+ " DAY)"
		" GROUP BY estado_reservatorio.estado_nome, estado_reservatorio.estado_sigla;")

	select_answer = IO.select_DB(query)

	keys = ["estado", "uf", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 "total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  "quant_reserv_intervalo_5"]

	list_dictionarys = funcoes_aux.list_of_dictionarys(select_answer, keys)

	# Semiarido Brasileiro
	volume_equivalente = 0
	capacidade_equivalente = 0
	porcentagem_equivalente = 0.0
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

	if capacidade_equivalente > 0:
		porcentagem_equivalente = volume_equivalente/capacidade_equivalente*100

	list_dictionarys.append({"estado":"Semiarido", "uf":"Semiarido","semiarido":"Semiárido Brasileiro", "volume_equivalente":round(volume_equivalente,2),
		"capacidade_equivalente":round(capacidade_equivalente,2), "porcentagem_equivalente":round(porcentagem_equivalente,1),
		"quant_reservatorio_com_info":quant_reservatorio_com_info,"quant_reservatorio_sem_info":quant_reservatorio_sem_info,
		"total_reservatorios":total_reservatorios, "quant_reserv_intervalo_1":quant_reserv_intervalo_1, "quant_reserv_intervalo_2":quant_reserv_intervalo_2,
		 "quant_reserv_intervalo_3":quant_reserv_intervalo_3, "quant_reserv_intervalo_4":quant_reserv_intervalo_4,
		 "quant_reserv_intervalo_5":quant_reserv_intervalo_5})

	return list_dictionarys


def reservoirs_equivalent_states_history(id_estado):
	if id_estado == 0 :
		query = ("SELECT date_format(data_informacao,'%d/%m/%Y'), round(sum(volume_equivalente),2), round(sum(capacidade_equivalente),2) as capacidade_equivalente, round((sum(volume_equivalente)/sum(capacidade_equivalente)*100),2), sum(quantidade_reservatorio_com_info), sum(quantidade_reservatorio_sem_info),"
	 			"sum(total_reservatorios), sum(intervalo_1), sum(intervalo_2), sum(intervalo_3), sum(intervalo_4),"
	  			"sum(intervalo_5) FROM mv_monitoramento_estado mv GROUP BY data_informacao DESC;")
		
		keys = ["data", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 	"total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  	"quant_reserv_intervalo_5"]
	else:
		query = ("SELECT date_format(data_informacao,'%d/%m/%Y'),estado, sigla, round(volume_equivalente,2), round(capacidade_equivalente,2), round(porcentagem_equivalente,2), CONVERT(quantidade_reservatorio_com_info, SIGNED), CONVERT(quantidade_reservatorio_sem_info, SIGNED),"
	 			"CONVERT(total_reservatorios, SIGNED), CONVERT(intervalo_1, SIGNED), CONVERT(intervalo_2, SIGNED), CONVERT(intervalo_3, SIGNED), CONVERT(intervalo_4, SIGNED),"
	  			"CONVERT(intervalo_5, SIGNED) FROM mv_monitoramento_estado mv WHERE mv.id_estado ="+str(id_estado)+" and volume_equivalente>0;")

		keys = ["data","estado", "uf", "volume_equivalente","capacidade_equivalente", "porcentagem_equivalente", "quant_reservatorio_com_info","quant_reservatorio_sem_info",
	 	"total_reservatorios", "quant_reserv_intervalo_1", "quant_reserv_intervalo_2", "quant_reserv_intervalo_3", "quant_reserv_intervalo_4",
	  	"quant_reserv_intervalo_5"]
	select_answer = IO.select_DB(query)
	

	list_dictionarys = funcoes_aux.list_of_dictionarys(select_answer, keys)


	return list_dictionarys


def reservoirs_equivalent_states_monitoring(uf="Semiarido"):

	list_dic = []
	list_dic_2 = []
	dates_list = [];
	date_final = datetime.strptime('31/12/1969', '%d/%m/%Y')
	inicial_date = datetime.today()
	volumes_list = []
	id_estado = 0

	keys_recentes = ["VolumePercentual","DataInformacao", "Volume"]
	keys = ['Volume','VolumePercentual',"total_reservatorios","quant_reservatorio_com_info","quant_reservatorio_sem_info","quant_reserv_intervalo_1","quant_reserv_intervalo_2","quant_reserv_intervalo_3","quant_reserv_intervalo_4","quant_reserv_intervalo_5",'DataInformacao']

	if uf == "AL": id_estado = 27
	elif uf == "BA": id_estado = 29
	elif uf == "CE": id_estado = 23
	elif uf == "MG": id_estado = 31
	elif uf == "PB": id_estado = 25
	elif uf == "PE": id_estado = 26
	elif uf == "PI": id_estado = 22
	elif uf == "RN": id_estado = 24
	elif uf == "SE": id_estado = 28
	elif uf == "BA": id_estado = 29


	dic = reservoirs_equivalent_states_history(id_estado)

	for elem in dic:
		date = datetime.strptime(elem["data"], '%d/%m/%Y')
		dates_list.insert(0,float(date.strftime('%s')))
		if elem["porcentagem_equivalente"] is not None:
			volumes_list.insert(0,elem["porcentagem_equivalente"])
		value = [elem["porcentagem_equivalente"], elem["data"], elem["volume_equivalente"]]
		value_2 = [elem["volume_equivalente"],elem["porcentagem_equivalente"],elem["total_reservatorios"], elem["quant_reservatorio_com_info"],elem["quant_reservatorio_sem_info"],elem["quant_reserv_intervalo_1"],elem["quant_reserv_intervalo_2"],elem["quant_reserv_intervalo_3"],elem["quant_reserv_intervalo_4"],elem["quant_reserv_intervalo_5"],elem["data"]]
		list_dic.insert(0,value)
		list_dic_2.insert(0,value_2)		

	regression_coefficient=0 #using gradient 0 for now
	if(len(volumes_list) == len(dates_list)):
		regression_gradient = funcoes_aux.regression_gradient(volumes_list,dates_list)
		if(not math.isnan(regression_gradient)):
			regression_coefficient=regression_gradient

	return {'volumes': funcoes_aux.list_of_dictionarys(list_dic_2, keys),'volumes_recentes':{'volumes':funcoes_aux.list_of_dictionarys(list_dic[len(list_dic)-7:-1], keys_recentes),
		'coeficiente_regressao': 0, 'data_final':date_final.strftime('%d/%m/%Y'), 'data_inicial':inicial_date.strftime('%d/%m/%Y')}}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_csv(req):
	reservatId = req.values["reservatId"]
	if 'file' not in req.files:
	    abort (404)
	file = req.files['file']
	if file.filename == '':
	    abort (404)
	if file and allowed_file(file.filename):
	    filename = secure_filename(file.filename)
	    monitoramento = file.read()
	    isValido = True
	    regex = re.compile(r"^\d+(.\d+)?,\d+(.\d+)?,[A-Z ]*,\d\d\/\d\d\/\d\d\d\d")
	    monitoramentoList = monitoramento.split('\r\n')
	    for i in range(1,len(monitoramentoList) -1):
	        if regex.search(monitoramentoList[i]) == None:
	            isValido = False
	    monitoramentoList = filter(lambda a: a != '', monitoramentoList)
	    saida = {"valido": isValido, "arquivo": file.filename, "linhas":len(monitoramentoList)}
	if isValido:
		temporary_upload(reservatId, monitoramentoList)
	return saida

def temporary_upload(reservatId, lines):
	IO.delete_DB_upload()
	values = []
	#id_reservatorio,cota,volume,volume_percentual,data_informacao,visualizacao,fonte
	for value in lines[1:]:
		aux = [reservatId] + value.split(',')
		values.append([int(reservatId),'',float(aux[1]),float(aux[2]),datetime.strptime(aux[4], '%d/%m/%Y').strftime('%Y-%m-%d'),1,aux[3]])
	IO.insert_many_BD_upload(values)

def confirm_upload(req,reservatId):
	# reservatId = req.values["reservatId"]
	return {'replaced' : IO.replace_reservat_history(reservatId)}

def city_info(sab=0):
	query = ("SELECT mu.id, mu.nome, mu.latitude,mu.longitude, es.sigla, es.nome from tb_municipio mu, tb_estado es where es.id=mu.id_estado and semiarido="+str(sab)+";")
	select_answer = IO.select_DB(query)

	keys = ["id_municipio","nome_municipio","latitude","longitude","UF","estado"]

	return funcoes_aux.list_of_dictionarys(select_answer, keys)

def search_information():
	query = ("SELECT r.id,r.nome,r.reservat as nome_exibicao,r.bacia,r.reservat"
		",GROUP_CONCAT(DISTINCT m.nome SEPARATOR ' / ') municipio"
		" FROM tb_reservatorio r JOIN tb_reservatorio_municipio rm ON r.id=rm.id_reservatorio"
		" JOIN tb_municipio m ON rm.id_municipio=m.id"
		" GROUP BY r.id;")

	select_answer = IO.select_DB(query)

	keys = ["id","nome", "nome_exibicao", "bacia","reservat","municipio"]

	answer = funcoes_aux.list_of_dictionarys(select_answer, keys, "info")

	query_2 = ("SELECT m.id,m.nome, CONCAT_WS(' - ', m.nome, e.sigla) nome_exibicao"
		" FROM tb_municipio m JOIN tb_estado e ON m.id_estado=e.id and m.semiarido=1")

	select_answer_2 = IO.select_DB(query_2)

	keys_2 = ["id","nome","nome_exibicao"]

	answer.extend(funcoes_aux.list_of_dictionarys(select_answer_2, keys_2, "mun"))

	return answer
