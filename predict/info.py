import sys
sys.path.append('../sab-api/script')
import aux_collection_insert

def cotas(reservatId):
    query = 'SELECT cota FROM tb_cav WHERE id = reservatId'
    cotas = aux_collection_insert.consulta_BD(query)
    return cotas

def volumes(reservatId):
    query = 'SELECT volume FROM tb_cav WHERE id = reservatId'
    volumes = aux_collection_insert.consulta_BD(query)
    return volumes

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
    c = cotas(reservatId)
    v = volumes(reservatId)
    va = volumeAtual(reservatId)
    index = maisProximo(reservatId, va, v)
    cota = ((c[index+1] - c[index]) * ((va - v[index]) / (v[index+1] - v[index]))) + c[index]
    return cota

def retirada(reservatId, mes):
    c = cotas(reservatId)
    evaporacao = evap(reservatId, mes) / 4
    cota = cota(reservatId)
    rt = c[0]
    if (cota - evaporacao) >= c[0]:
        rt = cota - evaporacao
    return rt

def volumeParcial(reservatId, mes):
    c = cotas(reservatId)
    v = volumes(reservatId)
    ca = retirada(reservatId)
    index = maisProximo(reservatId, ca, c)
    vp = ((v[index+1] - v[index]) * ((ca - c[index]) / (c[index+1] - c[index]))) + v[index]
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
        return mes
