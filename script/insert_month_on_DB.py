#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import requests
import MySQLdb
from datetime import datetime
from dateutil import relativedelta
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

# ADICIONAR VALORES DA CONSULTA DO MONITORAMENTO PARA QUANDO FOR INSERIR VERIFICAR SE VAI COMPARAR COM O ANTERIOR OU COM ELE
def define_picos(lista_reserv, ultimo_monitoramento):

	if(not ultimo_monitoramento[3] is None):
		ultimo_monitamento_lista = list(ultimo_monitoramento)
		data_lista = ultimo_monitamento_lista[4].split("-")
		ultimo_monitamento_lista[4] = '-'.join(list(reversed(data_lista)))

		lista_reservatorios=[ultimo_monitamento_lista]
		lista_reservatorios.extend(list(reversed(lista_reserv)))
	else:
		lista_reservatorios= list(reversed(lista_reserv))
	ultimoValorValido = None
	porcentagem = 25
	for m in range(len(lista_reservatorios)):
		if((m == 0)and (m+1 < len(lista_reservatorios)) and (ultimo_monitoramento[3] is None)):
			# VERIFICANDO SE ESTÁ FORA DO INTERVALO DE 60 DIAS
			if((datetime.strptime(lista_reservatorios[m][4], "%Y-%m-%d") <= (datetime.strptime(lista_reservatorios[m+1][4], "%Y-%m-%d")- relativedelta.relativedelta(days=60)))
				# VERIFICANDO SE ESTÁ DENTRO DA MARGEM DE 30% PRA MAIS OU PRA MENOS NA PORCENTAGEM
				or ((float(lista_reservatorios[m][3]) >= (float(lista_reservatorios[m+1][3])-porcentagem)) and (float(lista_reservatorios[m][3]) <= (float(lista_reservatorios[m+1][3])+porcentagem)))):
				ultimoValorValido = m
				lista_reservatorios[m][5] = 1

		elif(m > 0):
			if(ultimoValorValido is None):
				# VERIFICANDO SE ESTÁ FORA DO INTERVALO DE 60 DIAS
				if((datetime.strptime(lista_reservatorios[m][4], "%Y-%m-%d") >= (datetime.strptime(lista_reservatorios[m-1][4], "%Y-%m-%d") + relativedelta.relativedelta(days=60)))
				# VERIFICANDO SE ESTÁ DENTRO DA MARGEM DE 30% PRA MAIS OU PRA MENOS NA PORCENTAGEM
					or ((float(lista_reservatorios[m][3]) >= (float(lista_reservatorios[m-1][3])-porcentagem)) and (float(lista_reservatorios[m][3]) <= (float(lista_reservatorios[m-1][3])+porcentagem)))):
					ultimoValorValido = m
					lista_reservatorios[m][5] = 1

			else:
				# VERIFICANDO SE ESTÁ FORA DO INTERVALO DE 60 DIAS
				if(datetime.strptime(lista_reservatorios[m][4], "%Y-%m-%d") >= (datetime.strptime(lista_reservatorios[ultimoValorValido][4], "%Y-%m-%d") + relativedelta.relativedelta(days=60))
					# VERIFICANDO SE ESTÁ DENTRO DA MARGEM DE 30% PRA MAIS OU PRA MENOS NA PORCENTAGEM
					or ((float(lista_reservatorios[m][3]) >= (float(lista_reservatorios[ultimoValorValido][3])-porcentagem)) and 
						(float(lista_reservatorios[m][3]) <= (float(lista_reservatorios[ultimoValorValido][3])+porcentagem)))):
					ultimoValorValido = m
					lista_reservatorios[m][5] = 1
	if(not ultimo_monitoramento[3] is None):
		lista_reservatorios.pop(0)
	return lista_reservatorios




ultimos_monitoramentos = consulta_BD("SELECT mon.id, mo.cota, mo.volume, mo.volume_percentual, date_format(mo.data_informacao,'%d-%m-%Y') FROM tb_monitoramento mo RIGHT JOIN (SELECT r.id, max(m.data_informacao) AS maior_data FROM tb_reservatorio r LEFT OUTER JOIN tb_monitoramento m ON r.id=m.id_reservatorio GROUP BY r.id) mon ON mo.id_reservatorio=mon.id AND mon.maior_data=mo.data_informacao;")

formato_data_1 = '%d/%m/%Y'
formato_data_2 = '%d-%m-%Y'
formato_data_3 = '%Y-%m-%d'

data_final = str(datetime.now().strftime(formato_data_2))

cabecalho = ['Codigo','Reservatorio','Cota','Capacidade','Volume','VolumePercentual','DataInformacao']

for monitoramento in ultimos_monitoramentos:
	to_insert = []

	reserv = str(monitoramento[0])
	if (monitoramento[4] is None):
		data_inicial = "31-12-1969"
	else: 
		data_inicial = str(monitoramento[4])

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
				to_insert.append([id_reservatorio,cota,volume,volumePercentual,dataInformacao,0])

			json_insert={}

	if(len(to_insert) >0):
		insert_many_BD(define_picos(to_insert, monitoramento))
		
	time.sleep(1)
