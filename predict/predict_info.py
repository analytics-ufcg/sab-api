import sys
sys.path.append('../sab-api/script')
import aux_collection_insert

from datetime import timedelta, date, datetime

listaCotas = []
listaVolumes = []
data = ''
mes = ''
evaporacao = 0.0

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

def popular_variaveis(reservatId, data_inicial):
    global listaCotas
    listaCotas = cotas(reservatId)
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
    for i in range(0, len(listValues)):
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

def cota(vol):
    lv = listaVolumes
    lc = listaCotas
    v_atual = float(vol)
    index = maisProximo(v_atual, lv)
    ct = ((lc[index+1] - lc[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + lc[index]
    return ct

def cotaEvap(reservatId, vol):
    lc = listaCotas
    c_atual = cota(vol)
    c_final = lc[0]
    if (c_atual - evaporacao) >= lc[0]:
        c_final = c_atual - evaporacao
    return c_final

def volumeParcial(reservatId, data_atual, vol):
    global data
    data = data_atual
    if mes != data.month:
        global mes
        mes = data.month
        global evaporacao
        evaporacao = evap(reservatId)

    lc = listaCotas
    lv = listaVolumes
    c_final = cotaEvap(reservatId, vol)
    index = maisProximo(c_final, lc)
    vp = ((lv[index+1] - lv[index]) * ((c_final - lc[index]) / (lc[index+1] - lc[index]))) + lv[index]
    return vp

def demanda(reservatId):
    query = """SELECT demanda FROM tb_reservatorio WHERE id="""+str(reservatId)
    dem = aux_collection_insert.consulta_BD(query)
    return float(dem[0][0]) if len(dem) > 0 and dem[0][0] != None else None

def volumeMorto(reservatId):
    query = 'SELECT volume_morto FROM tb_reservatorio WHERE id = ' + str(reservatId)
    row = aux_collection_insert.consulta_BD(query)[0][0]
    return row
