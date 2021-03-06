import sys
sys.path.append('../sab-api/script')
import aux_collection_insert

from datetime import timedelta, date, datetime

listaAreas = []
listaVolumes = []
evapDiv = 1

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

def maisProximo(value, listValues):
    mpValue = listValues[0]
    index = 0
    for i in range(0, len(listValues)-1):
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

def evap(mes, reservatId):
    mes_dic = {'1' : 'jan', '2' : 'fev', '3' : 'mar', '4' : 'abr', '5' : 'mai', '6' : 'jun',
               '7' : 'jul', '8' : 'ago', '9' : 'set', '10' : 'out', '11' : 'nov', '12' : 'dez'}
    query = 'SELECT eva_' + mes_dic[str(mes)] + ' FROM tb_reservatorio WHERE id = '+str(reservatId)
    rows = aux_collection_insert.consulta_BD(query)
    evaporacao = rows[0][0] if len(rows) > 0 else 0.0
    return (evaporacao / 1000.0) / evapDiv if evaporacao != None else 0.0

def area(vol, reservatId):
    lv = listaVolumes
    la = listaAreas
    v_atual = float(vol)
    index = maisProximo(v_atual, lv)
    ar= ((la[index+1] - la[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + la[index]
    return ar

def areaEvap(mes, vol, reservatId):
    evaporacao = evap(mes, reservatId)
    area_atual = area(vol, reservatId)
    evap_real = area_atual * evaporacao
    return evap_real

def volumeParcial(mes, vol, reservatId):
    evap_real = areaEvap(mes, vol, reservatId)
    vp = vol - evap_real
    return vp

def rowsToList(rows):
    lista = []
    lista_externa = list(rows)
    if len(lista_externa) > 0:
        for li in lista_externa:
            aux = list(li)
            if len(aux) > 1:
                lista.append(aux[0])
                lista.append(aux[1])
            else:
                lista.append(aux[0])
        return lista
    else:
        return lista

def demandas(data, reservatId):
    mes_atual = int(data.month)
    mes_limite = mes_atual - 12
    ano_atual = int(data.year)
    if mes_limite > 0:
        ano_limite = ano_atual
    else:
        ano_limite = ano_atual - 1
        mes_limite = 12 + mes_limite

    ld = []

    query = """SELECT data_informacao, volume FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
            data_informacao BETWEEN '"""+str(ano_limite)+"""-"""+str(mes_limite)+"""-01' AND '"""+str(ano_atual)+"""-"""+str(mes_atual)+"""-31' ORDER BY data_informacao ASC"""
    rows = rowsToList(aux_collection_insert.consulta_BD(query))

    if (len(listaAreas) <= 0) or (len(listaVolumes) <= 0):
        demanda_res = "NULL"
        query = """UPDATE tb_reservatorio SET demanda="""+str(demanda_res)+""" WHERE id="""+str(reservatId)
        aux_collection_insert.update_BD(query)

    elif len(rows) > 0:
        lista_datas = []
        lista_dias = []
        lista_volumes = []

        for i in range(0, len(rows)-3, 2):
            data_inicial = rows[i]
            data_final = rows[i+2]
            vol_inicial = rows[i+1]
            vol_final = rows[i+3]
            dif_datas = data_final - data_inicial

            if (float(vol_inicial) > float(vol_final)) and (dif_datas.days <= 30):
                if data_inicial not in lista_datas:
                    lista_dias.append(data_inicial)
                if data_final not in lista_datas:
                    lista_dias.append(data_final)
                lista_volumes.append([vol_inicial, vol_final])
                lista_datas.append([data_inicial, data_final])

        lista_dem = []
        for j in range(len(lista_volumes)):
            evapDiv_inicial = 0
            evapDiv_final = 0

            mes_inicial = int(lista_datas[j][0].month)
            for data in lista_dias:
                evapDiv_inicial += 1 if mes_inicial == int(data.month) else 0
            global evapDiv
            evapDiv = evapDiv_inicial
            vp_inicial = volumeParcial(mes_inicial, float(lista_volumes[j][0]) * 1000000.00, reservatId)

            mes_final = int(lista_datas[j][1].month)
            for data in lista_dias:
                evapDiv_final += 1 if mes_final == int(data.month) else 0
            global evapDiv
            evapDiv = evapDiv_inicial
            vp_final = volumeParcial(mes_final, float(lista_volumes[j][1]) * 1000000.00, reservatId)

            dif_datas = lista_datas[j][1] - lista_datas[j][0]
            dem = (vp_inicial - vp_final) / dif_datas.days
            lista_dem.append(dem)

        demanda_res = sum(lista_dem) / len(lista_dem) if len(lista_dem) > 0 else "NULL"
        return demanda_res

def popular_demanda(reservatId):
    global listaAreas
    listaAreas = areas(reservatId)
    global listaVolumes
    listaVolumes = volumes(reservatId)
