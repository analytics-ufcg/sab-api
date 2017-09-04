#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aux_collection_insert
import csv
from unicodedata import normalize
from datetime import timedelta, date, datetime

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

reader_outorgas_pb = csv.DictReader(open('../data/outorgas_pb.csv'))
outorgas_pb = {}
resertvats = nomes_PB()
for row in reader_outorgas_pb:
    for column, value in row.iteritems():
        outorgas_pb.setdefault(column, []).append(value)
    for res in resertvats:
        if remove_accents(outorgas_pb["Açude Monitorados"][0]) == remove_accents(res[0]):
            print outorgas_pb["Açude Monitorados"][0]
    outorgas_pb = {}
