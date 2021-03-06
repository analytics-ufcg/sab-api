#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta
import numpy
import MySQLdb


# ADICIONAR VALORES DA CONSULTA DO MONITORAMENTO PARA QUANDO FOR INSERIR VERIFICAR SE VAI COMPARAR COM O ANTERIOR OU COM ELE
def retira_ruido(lista_reserv, ultimo_monitoramento, fonte):
	diasRange = relativedelta.relativedelta(days=60)
	if(not ultimo_monitoramento[3] is None):
		ultimo_monitamento_lista = list(ultimo_monitoramento)
		data_lista = ultimo_monitamento_lista[4].split("-")
		ultimo_monitamento_lista[4] = '-'.join(list(reversed(data_lista)))

		lista_reservatorios=[ultimo_monitamento_lista]
		lista_reservatorios.extend(list(reversed(lista_reserv)))
	else:
		lista_reservatorios= list(reversed(lista_reserv))

	for m in range(len(lista_reservatorios)):
		valores = []
		valoresAnteriores = []
		valoresPosteriores = []
		porcentagemAtual = float(lista_reservatorios[m][3])
		for reserv in range(len(lista_reservatorios)):
			# VERIFICA SE ESTÁ DENTRO DO VALOR DO RANGE
			if((datetime.strptime(lista_reservatorios[m][4], "%Y-%m-%d") <= (datetime.strptime(lista_reservatorios[reserv][4], "%Y-%m-%d")+ diasRange))
				and ((datetime.strptime(lista_reservatorios[m][4], "%Y-%m-%d") >= (datetime.strptime(lista_reservatorios[reserv][4], "%Y-%m-%d")- diasRange)))):
				# VERIFICA SE O VALOR É ANTERIOR OU POSTERIOR
				if(m > reserv):
					if(int(lista_reservatorios[reserv][5]) == 1):
						valoresAnteriores.append(float(lista_reservatorios[reserv][3]))
				else:
					valoresPosteriores.append(float(lista_reservatorios[reserv][3]))
		# VERIFICA SE TEM A MESMA QUANTIDADE DE VALORES ANTERIORES E POSTERIORES
		if(len(valoresAnteriores) == len(valoresPosteriores) or len(valoresAnteriores) == 0 or len(valoresPosteriores) == 0):
			valores.extend(valoresAnteriores)
			valores.extend(valoresPosteriores)
		elif(len(valoresAnteriores) < len(valoresPosteriores)):
			valores.extend(valoresAnteriores)
			for i in range(len(valoresAnteriores)):
				valores.append(valoresPosteriores[i])
		else:
			for i in range(len(valoresPosteriores), -1, -1):
				valores.append(valoresAnteriores[i])
			valores.extend(valoresPosteriores)
		# VERIFICA SE O DADO NÃO É ISOLADO
		if(len(valores) > 0):
			desvioPadrao = numpy.std(valores)
			if (desvioPadrao>30):
				intervalo = desvioPadrao
			else:
				intervalo = desvioPadrao+10
			media = numpy.mean(valores)
			if((porcentagemAtual <= media+intervalo) and (porcentagemAtual >= media-intervalo) and porcentagemAtual <= 150):
				lista_reservatorios[m].append(1)
			else:
				lista_reservatorios[m].append(0)
		else:
			lista_reservatorios[m].append(1)
		lista_reservatorios[m].append(fonte)
	if(not ultimo_monitoramento[3] is None):
		lista_reservatorios.pop(0)

	return lista_reservatorios


def consulta_BD(query):
	""" Connect to MySQL database """
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	rows = []
	try:
		cursor.execute(query)
		rows = cursor.fetchall()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	cursor.close()
	conn.close()

	return rows

def insert_many_BD(values):
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	try:
		cursor.executemany("""INSERT IGNORE INTO tb_monitoramento (id_reservatorio,cota,volume,volume_percentual,data_informacao,visualizacao,fonte) VALUES (%s,%s,%s,%s,%s,%s,%s)""", values)
		conn.commit()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	cursor.close()
	conn.close()

def insert_many_BD_uhe(values):
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	try:
		cursor.executemany("""INSERT IGNORE INTO tb_monitoramento_uhe (id_reservatorio,volume_util_acumulado,cota,afluencia,defluencia,data_informacao,fonte) VALUES (%s,%s,%s,%s,%s,%s,%s)""", values)
		conn.commit()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	cursor.close()
	conn.close()

def update_BD(query):
	""" Connect to MySQL database """
	conn = MySQLdb.connect(read_default_group='INSA',db="INSA")
	cursor = conn.cursor()
	try:
		cursor.execute(query)
		conn.commit()
	except MySQLdb.Error as e:
		print "Error", e
		conn.rollback()

	cursor.close()
	conn.close()
