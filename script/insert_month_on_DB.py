#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import requests
import MySQLdb
from datetime import datetime
import time

reload(sys)
sys.setdefaultencoding('utf8')


def consulta_BD(query):
	""" Connect to MySQL database """
	try:
		conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
		cursor = conn.cursor()

		cursor.execute(query)

		rows = cursor.fetchall()

	finally:
		cursor.close()
		conn.close()
	
	return rows

def insert_many_BD(values):
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	try:
		cursor.executemany("""INSERT INTO tb_monitoramento (id_reservatorio,cota,volume,volume_percentual,data_informacao,visualizacao) VALUES (%s,%s,%s,%s,%s,%s)""", values)
		conn.commit()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	cursor.close()
	conn.close()


ultimos_monitoramentos = consulta_BD("SELECT r.id, date_format(MAX(m.data_informacao),'%d-%m-%Y') FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id;")

formato_data_1 = '%d/%m/%Y'
formato_data_2 = '%d-%m-%Y'
formato_data_3 = '%Y-%m-%d'

data_final = str(datetime.now().strftime(formato_data_2))

cabecalho = ['Codigo','Reservatorio','Cota','Capacidade','Volume','VolumePercentual','DataInformacao']

for monitoramento in ultimos_monitoramentos:
	to_insert = []

	reserv = str(monitoramento[0])
	if (monitoramento[1] is None):
		data_inicial = "31-12-1969"
	else: 
		data_inicial = str(monitoramento[1])

	r = requests.get('http://sar.ana.gov.br/Medicao/GridMedicoes?DropDownListReservatorios='+reserv+'&dataInicialInformada='+data_inicial+'&dataFinalInformada='+data_final+'&cliqueiEmPesquisar=true')

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
				id_reservatorio = int(json_insert["Codigo"])
				to_insert.append((id_reservatorio,cota,volume,volumePercentual,dataInformacao,1))

			json_insert={}

	if(to_insert >0):
		insert_many_BD(to_insert)
		
	time.sleep(1)
