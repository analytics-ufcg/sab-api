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

def demanda_dif(reservatId, data, volumeAtual):
    lastWeek = data - timedelta(days=7)
    query = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
            data_informacao='"""+str(lastWeek)+"""' GROUP BY volume """
    rows = rowsToList(aux_collection_insert.consulta_BD(query))

    if len(rows) <= 0:
            query = """SELECT volume, MAX(data_informacao) FROM tb_monitoramento
                    WHERE id_reservatorio="""+str(reservatId)+""" AND
                    data_informacao=(SELECT MAX(data_informacao)
                                    FROM tb_monitoramento
                                    WHERE id_reservatorio="""+str(reservatId)+""") GROUP BY volume"""
            rows = rowsToList(aux_collection_insert.consulta_BD(query))

    dif_datas = data - rows[1]
    day = dif_datas.days
    media_dem = ((float(rows[0]) * 10000.00) - float(volumeAtual)) / day

    return media_dem if media_dem > 0.0 else 0.0

def critical(reservatId):
    query = 'SELECT capacidade FROM tb_reservatorio WHERE id = ' + str(reservatId)
    row = aux_collection_insert.consulta_BD(query)[0][0]
    cap = float(row) * 1000000.00
    critico = (cap * 8.0) / 100.0

    return critico
