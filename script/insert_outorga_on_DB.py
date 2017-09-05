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

def insert_outorga(outorgas_pb, resertvats):
    today = date.today()
    for res in resertvats:
        acude = outorgas_pb["Açude Monitorados"][0]
        expira = outorgas_pb["Expiração da Outorga"][0]
        vazao = outorgas_pb["Vazão Horária  (m³/h)"][0]

        if remove_accents(acude) == remove_accents(res[0]) and expira != "null" and vazao != "null":
            data = datetime.strptime(outorgas_pb["Expiração da Outorga"][0], "%d/%m/%Y").date()
            if data.year >= 2010:
                vazao = float(vazao) * 24.00
                if outorgas.get(acude) != None:
                    if data > today and outorgas[acude][0] > today:
                        vazao = outorgas[acude][1] + vazao
                        global outorgas
                        outorgas[acude] = [data, vazao]
                    elif data > outorgas[acude][0]:
                        global outorgas
                        outorgas[acude] = [data, vazao]
                else:
                    global outorgas
                    outorgas[acude] = [data, vazao]
                query = """UPDATE tb_reservatorio SET outorga="""+str(outorgas[acude][1])+""" WHERE id="""+str(res[1])
                aux_collection_insert.update_BD(query)

def popular_outorga():
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
