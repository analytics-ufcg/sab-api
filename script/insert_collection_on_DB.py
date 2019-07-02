#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import time
import aux_collection_insert
import urllib3


reload(sys)
sys.setdefaultencoding('utf8')
urllib3.disable_warnings()


ultimos_monitoramentos = aux_collection_insert.consulta_BD("SELECT mon.id, mo.cota, mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d-%m-%Y') FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id, max(m.data_informacao) AS maior_data FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao;")

formato_data_1 = '%d/%m/%Y'
formato_data_2 = '%d-%m-%Y'
formato_data_3 = '%Y-%m-%d'

data_final = str(datetime.now().strftime(formato_data_2))

cabecalho = ['Codigo','Reservatorio','Cota','Capacidade','Volume','VolumePercentual','DataInformacao']

# aux_collection_insert.update_BD("UPDATE tb_user_reservatorio SET atualizacao_reservatorio = 0;")

for monitoramento in ultimos_monitoramentos:
	to_insert = []

	reserv = str(monitoramento[0])
	if reserv in ('19123','19116','19122','19124','19125','19121','19126'):
		continue
	if (monitoramento[4] is None):
		data_inicial = "31-12-1969"
	else:
		data_inicial = str(monitoramento[4])

	try:
		r = requests.get('https://www.ana.gov.br/sar0/Medicao?dropDownListReservatorios='+reserv+'&dataInicial='+data_inicial+'&dataFinal='+data_final+'&button=Buscar', verify=False)
	except requests.exceptions.RequestException as e:  # This is the correct syntax
		print e
		continue	

	json_insert = {}
	contador_coluna = 0

	soup = BeautifulSoup(r.text.encode('utf8'), 'html.parser')
	for link in soup.find_all('td'):
		if(contador_coluna < len(cabecalho)):
			json_insert[cabecalho[contador_coluna]] = link.get_text().strip()
			contador_coluna +=1
		if(contador_coluna == len(cabecalho)):
			contador_coluna = 0

			if (datetime.strptime(data_inicial, formato_data_2) < datetime.strptime(json_insert["DataInformacao"], formato_data_1)):
				cota = json_insert["Cota"].replace(",", ".")
				volume = json_insert["Volume"].replace(",", ".")
				volumePercentual = json_insert["VolumePercentual"].replace(",", ".")
				dataInformacao = datetime.strptime(json_insert["DataInformacao"], formato_data_1).strftime(formato_data_3)
				id_reservatorio = reserv
				to_insert.append([id_reservatorio,cota,volume,volumePercentual,dataInformacao])

			json_insert={}

	if(len(to_insert) >0):
		aux_collection_insert.update_BD("UPDATE tb_user_reservatorio SET atualizacao_reservatorio = 1 WHERE id_reservatorio="+reserv+";")
		aux_collection_insert.insert_many_BD(aux_collection_insert.retira_ruido(to_insert, monitoramento, "ANA"))

	time.sleep(5)
