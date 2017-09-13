#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aux_collection_insert
import csv
from unicodedata import normalize
from datetime import timedelta, date, datetime

outorgas = {}

def remove_accents(txt):
	if (type(txt) is str):
		txt= unicode(txt, "utf-8")
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def nomes_PB():
    query = """SELECT DISTINCT res.nome, res.id
               FROM INSA.tb_reservatorio res,
                INSA.tb_reservatorio_municipio rm,
                INSA.tb_municipio mu,
                INSA.tb_estado es
               WHERE (
                res.id = rm.id_reservatorio AND
                rm.id_municipio = mu.id AND
                mu.id_estado = es.id AND
                es.sigla = 'PB'
               )
               ORDER BY res.nome ASC"""
    rows = aux_collection_insert.consulta_BD(query)
    return rows

def check_data(acude, listaDados):
	for i in range(0, len(outorgas[acude])):
		if outorgas[acude][i][1] == listaDados[0][1] and outorgas[acude][i][2] == listaDados[0][2] and outorgas[acude][i][3] == listaDados[0][3] and outorgas[acude][i][4] == listaDados[0][4]:
			return i
	return None

def sum_vazao(acude):
	vazao = 0
	for listaInterna in outorgas[acude]:
		vazao += listaInterna[1]
	return vazao

def insert_outorga(outorgas_pb, resertvats):
	today = date.today()
	for res in resertvats:
		acude = outorgas_pb["Açude Monitorados"][0]
		expira = outorgas_pb["Expiração da Outorga"][0]
		vazao = outorgas_pb["Vazão Horária  (m³/h)"][0]
		latitude = outorgas_pb["Latitude"][0]
		longitude = outorgas_pb["Longitude"][0]
		uso = outorgas_pb["Tipo de Uso"][0]
		listaDados = []

		if remove_accents(acude) == remove_accents(res[0]) and expira != "null" and vazao != "null":
			data = datetime.strptime(outorgas_pb["Expiração da Outorga"][0], "%d/%m/%Y").date()
			vazao = float(vazao) * 24.00
			listaDados.append([data, vazao, latitude, longitude, remove_accents(uso)])

			if outorgas.get(acude) != None:
				index = check_data(acude, listaDados)
				if index != None:
					if outorgas[acude][index][0] < listaDados[0][0]:
						global outorgas
						outorgas[acude][index] = listaDados[0]
				else:
					global outorgas
					outorgas[acude].append(listaDados[0])
			else:
				global outorgas
				outorgas[acude] = [[data, vazao, latitude, longitude, remove_accents(uso)]]

			vazao_total = sum_vazao(acude)
			query = """UPDATE tb_reservatorio SET outorga="""+str(vazao_total)+""" WHERE id="""+str(res[1])
			aux_collection_insert.update_BD(query)

#def popular_outorga():
reader_outorgas_pb = csv.DictReader(open('../data/outorgas_pb.csv'))
outorgas_pb = {}
resertvats = nomes_PB()
for row in reader_outorgas_pb:
    for column, value in row.iteritems():
        outorgas_pb.setdefault(column, []).append(value)
    insert_outorga(outorgas_pb, resertvats)
    outorgas_pb = {}

def create_outorga():
    query = """ALTER TABLE tb_reservatorio ADD COLUMN outorga MEDIUMTEXT NULL AFTER demanda"""
    aux_collection_insert.update_BD(query)
