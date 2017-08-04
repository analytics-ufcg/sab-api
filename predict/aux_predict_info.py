import sys
sys.path.append('../sab-api/script')
import aux_collection_insert

from datetime import timedelta, date, datetime

def cotas(reservatId):
    query = 'SELECT cota FROM tb_cav WHERE id_reservatorio = ' + str(reservatId)
    cotas = aux_collection_insert.consulta_BD(query)
    aux = list(cotas)
    list_of_cotas = []
    for value in aux:
        list_of_cotas.append(value[0])
    return list_of_cotas

def volumes(reservatId):
    query = 'SELECT volume FROM tb_cav WHERE id_reservatorio = ' + str(reservatId)
    volumes = aux_collection_insert.consulta_BD(query)
    aux = list(volumes)
    list_of_volumes = []
    for value in aux:
        list_of_volumes.append(value[0])
    return list_of_volumes

def rowsToList(rows):
    lista = []
    lista_externa = list(rows)
    if len(lista_externa) > 0:
        aux = list(lista_externa[0])
        lista.append(aux[0])
        lista.append(aux[1])
        return lista
    else:
        return lista

def critical(reservatId):
    query = 'SELECT capacidade FROM tb_reservatorio WHERE id = ' + str(reservatId)
    row = aux_collection_insert.consulta_BD(query)[0][0]
    cap = float(row) * 1000000.00
    critico = (cap * 8.0) / 100.0

    return critico
