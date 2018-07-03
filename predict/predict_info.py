#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../sab-api/script')
import aux_collection_insert
import retirada
import numpy

from datetime import timedelta, date, datetime

listaAreas = []
listaVolumes = []
data = ''
mes = ''
evaporacao = 0.0

def areas(reservatId):
    query = 'SELECT area FROM tb_cav WHERE id_reservatorio = ' + str(reservatId)
    areas = aux_collection_insert.consulta_BD(query)
    aux = list(areas)
    list_of_areas = []
    for value in aux:
        list_of_areas.append(value[0])
    return list_of_areas

def volumes(reservatId):
    query = 'SELECT volume FROM tb_cav WHERE id_reservatorio = ' + str(reservatId)
    volumes = aux_collection_insert.consulta_BD(query)
    aux = list(volumes)
    list_of_volumes = []
    for value in aux:
        list_of_volumes.append(value[0])
    return list_of_volumes

def popular_variaveis(reservatId, data_inicial):
    global listaAreas
    listaAreas = areas(reservatId)
    global listaVolumes
    listaVolumes = volumes(reservatId)
    global data
    data = data_inicial
    global mes
    mes = data.month
    global evaporacao
    evaporacao = evap(reservatId)

def maisProximo(value, listValues):
    mpValue = listValues[0]
    index = 0
    for i in range(0, len(listValues) -1):
        if value == listValues[i]:
            mpValue = listValues[i]
            index = i
            return index
        elif mpValue <= listValues[i] and value > listValues[i]:
             mpValue = listValues[i]
             index = i
        else:
            break
    return index

def precip():
    query = ''
    pt = 0
    return pt

def vazao():
    query = ''
    qt = 0
    return qt

def evap(reservatId):
    mes_evap = int(mes)
    ano_evap = int(data.year)

    mes_dic = {'1' : 'jan', '2' : 'fev', '3' : 'mar', '4' : 'abr', '5' : 'mai', '6' : 'jun',
               '7' : 'jul', '8' : 'ago', '9' : 'set', '10' : 'out', '11' : 'nov', '12' : 'dez'}
    query = 'SELECT eva_' + mes_dic[str(mes_evap)] + ' FROM tb_reservatorio WHERE id = ' + str(reservatId)
    rows = aux_collection_insert.consulta_BD(query)
    evaporacao = rows[0][0]
    if len(rows) < 0 or evaporacao == None:
        evaporacao = 0.0

    if mes_evap == 2:
        if ((ano_evap % 4) == 0 and (ano_evap % 100) != 0) or (ano_evap % 400) == 0:
            return (evaporacao / 1000.0) / 29
        return (evaporacao / 1000.0) / 28
    elif (mes_evap % 2) == 0:
        return (evaporacao / 1000.0) / 31
    elif mes_evap == 7:
        return (evaporacao / 1000.0) / 31
    return (evaporacao / 1000.0) / 30

def area(vol):
    lv = listaVolumes
    la = listaAreas
    v_atual = float(vol)
    index = maisProximo(v_atual, lv)
    ar= ((la[index+1] - la[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + la[index]
    return ar

def evapReal(reservatId, vol):
    a_atual = area(vol)
    evap_real = a_atual * (evaporacao / 2.0)
    return evap_real

def volumeParcial(reservatId, data_atual, vol):
    global data
    data = data_atual
    if mes != data.month:
        global mes
        mes = data.month
        global evaporacao
        evaporacao = evap(reservatId)

    evap_real = evapReal(reservatId, vol)
    vp = vol - evap_real
    return vp

#Retorno em m³
def demanda(data, reservatId):
    retirada.popular_demanda(reservatId)
    dem = retirada.demandas(data, reservatId)
    return dem if type(dem) == float else None

#Retorno em m³
def volumeMorto(reservatId):
    query = 'SELECT volume_morto FROM tb_reservatorio WHERE id = ' + str(reservatId)
    row = aux_collection_insert.consulta_BD(query)[0][0]
    return row

#Retorno em m³, recebe do bd em hm³
def volumeAtual(reservatId):
    query = 'SELECT volume FROM mv_monitoramento WHERE id_reservatorio = ' + str(reservatId)
    row = aux_collection_insert.consulta_BD(query)[0][0]
    return float(row) * 1000000.0

def volumePassado(reservatId, ultimaData):
    query = 'SELECT volume FROM tb_monitoramento WHERE id_reservatorio = ' + str(reservatId) + ' ORDER BY ABS(DATEDIFF(data_informacao, \'' + str(ultimaData) + '\')) LIMIT 1'
    row = aux_collection_insert.consulta_BD(query)[0][0]
    return float(row) * 1000000.0

def volumesEntre(reservatId, inicio, fim):
    query = """SELECT data_informacao, volume FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
            data_informacao BETWEEN '"""+str(inicio)+"""' AND '"""+str(fim)+"""' ORDER BY data_informacao ASC"""
    rows = aux_collection_insert.consulta_BD(query)
    return rows

#Retorno em m³
def outorga(reservatId):
    query = """SELECT outorga FROM tb_reservatorio WHERE id="""+str(reservatId)
    dem = aux_collection_insert.consulta_BD(query)
    return float(dem[0][0]) if len(dem) > 0 and dem[0][0] != None else None

#Retorna última data
def getDate(reservatId):
    query = "SELECT data_informacao FROM INSA.mv_monitoramento WHERE id_reservatorio="+str(reservatId)
    date = aux_collection_insert.consulta_BD(query)[0][0]
    return date

def getClosestDate(reservatId, date):
    query = "select data_informacao from INSA.tb_monitoramento WHERE data_informacao >= '"+str(date)+"' AND id_reservatorio = "+str(reservatId)+" ORDER BY data_informacao LIMIT 1"
    date = aux_collection_insert.consulta_BD(query)[0][0]
    return date

#Retorna série de volumes
def getSeries(reservatId, data):
    query = 'SELECT volume FROM tb_monitoramento WHERE id_reservatorio = ' + str(reservatId) + ' AND data_informacao <= \'' + str(data) + '\''
    row = aux_collection_insert.consulta_BD(query)
    series = []
    for vol in row:
        series.append(float(vol[0]))
    return series

# create a differenced series
def difference(dataset, interval=1.0):
	diff = list()
	for i in range(interval, len(dataset)):
		value = dataset[i] - dataset[i - interval]
		diff.append(value)
	return numpy.array(diff)

# invert differenced value
def inverse_difference(history, yhat, interval=1):
	return yhat + history[-interval]

def getCapacidade(reservatId):
    query = "SELECT capacidade FROM tb_reservatorio WHERE id="""+str(reservatId)
    cap = aux_collection_insert.consulta_BD(query)[0][0]
    return cap
