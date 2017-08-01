import sys
sys.path.append('../sab-api/script')
import aux_collection_insert
import aux_predict_info

listaCotas = []
listaVolumes = []

def popular_variaveis(reservatId):
    global listaCotas
    listaCotas = aux_predict_info.cotas(reservatId)
    global listaVolumes
    listaVolumes = aux_predict_info.volumes(reservatId)

def maisProximo(reservatId, value, listValues):
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

def evap(reservatId, mes):
    mes_dic = {'1' : 'jan', '2' : 'fev', '3' : 'mar', '4' : 'abr', '5' : 'mai', '6' : 'jun',
               '7' : 'jul', '8' : 'ago', '9' : 'set', '10' : 'out', '11' : 'nov', '12' : 'dez'}
    query = 'SELECT eva_' + mes_dic[str(mes)] + ' FROM tb_reservatorio WHERE id = ' + str(reservatId)
    evaporacao = aux_collection_insert.consulta_BD(query)[0][0]
    return evaporacao / 1000.0

def cota(reservatId, vol):
    lv = listaVolumes
    lc = listaCotas
    v_atual = float(vol)
    index = maisProximo(reservatId, v_atual, lv)
    ct = ((lc[index+1] - lc[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + lc[index]
    return ct

def cotaEvap(reservatId, mes, vol):
    lc = listaCotas
    evaporacao = evap(reservatId, mes) / 4
    c_atual = cota(reservatId, vol)
    c_final = lc[0]
    if (c_atual - evaporacao) >= lc[0]:
        c_final = c_atual - evaporacao
    return c_final

def volumeParcial(reservatId, mes, vol):
    lc = listaCotas
    lv = listaVolumes
    c_final = cotaEvap(reservatId, mes, vol)
    index = maisProximo(reservatId, c_final, lc)
    vp = ((lv[index+1] - lv[index]) * ((c_final - lc[index]) / (lc[index+1] - lc[index]))) + lv[index]
    return vp

def demanda(reservatId, data, vol):
    dif_volumes = aux_predict_info.demanda_dif(reservatId, data, vol)
    demanda = dif_volumes - evap(reservatId, data.month)
    return demanda
