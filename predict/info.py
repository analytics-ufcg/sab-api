import sys
sys.path.append('../sab-api/script')
import aux_collection_insert

listaCotas = []
listaVolumes = []

def cotas(reservatId):
    query = 'SELECT cota FROM tb_cav WHERE id = reservatId'
    cotas = aux_collection_insert.consulta_BD(query)
    return cotas

def volumes(reservatId):
    query = 'SELECT volume FROM tb_cav WHERE id = reservatId'
    volumes = aux_collection_insert.consulta_BD(query)
    return volumes

def popular_variaveis(reservatId):
    global listaCotas
    listaCotas = cotas(reservatId)
    global listaVolumes
    listaVolumes = volumes(reservatId)

def maisProximo(reservatId, value, listValues):
    mpValue = listValues[0]
    index = 0
    for i = 0; len(listValues) - 1; i++:
        if value == listValues[i]:
            mpValue = listValues[i]
            index = i
            return index
        elif mpValue <= listValues[i] && value > listValues[i]:
             mpValue = listValues[i]
             index = i
        else:
            break
    return index

def volumeAtual(reservatId):
    query = '''SELECT r.volume FROM tb_reservatorio r
            WHERE r.data_informacao = (SELECT MAX(rt.data_informacao)
            FROM tb_reservatorio rt WHERE (rt.id_reservatorio = reservatId AND
            rt.id_reservatorio = reservatId))'''
    va = aux_collection_insert.consulta_BD(query)
    return va

def precip():
    query = ''
    pt = 0
    return pt

def vazao():
    query = ''
    qt = 0
    return qt

def evap(reservatId, mes):
    query = ''
    et = aux_collection_insert.consulta_BD(query)
    return et

def cota(reservatId):
    lv = listaVolumes
    lc = listaCotas
    va = volumeAtual(reservatId)
    index = maisProximo(reservatId, va, lv)
    cota = ((lc[index+1] - lc[index]) * ((va - lv[index]) / (lv[index+1] - lv[index]))) + lc[index]
    return cota

def cotaEvap(reservatId, mes):
    c = listaCotas
    evaporacao = evap(reservatId, mes) / 4
    cota = cota(reservatId, c)
    rt = c[0]
    if (cota - evaporacao) >= c[0]:
        rt = cota - evaporacao
    return rt

def volumeParcial(reservatId, mes):
    lc = listaCotas
    lv = listaVolumes
    c_evap = cotaEvap(reservatId, mes)
    index = maisProximo(reservatId, ca, lc)
    vp = ((lv[index+1] - lv[index]) * ((ca - lc[index]) / (lc[index+1] - lc[index]))) + lv[index]
    return vp

def demanda(reservatId, today, lastWeek):
    query = 'SELECT volume FROM tb_reservatorio WHERE (id_reservatorio = reservatId AND data_informacao = lastWeek)'
    v_antes = aux_collection_insert.consulta_BD(query)
    v_atual = volumeAtual(reservatId)
    if v_antes <= v_atual:
        return 0
    else:
        mes = today.month()
        demanda = v_antes - v_atual - evap(reservatId, mes)
        return demanda
