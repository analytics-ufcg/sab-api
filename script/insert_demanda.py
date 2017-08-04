import aux_collection_insert
from datetime import timedelta, date, datetime


def cotas():
    query = 'SELECT cota FROM tb_cav WHERE id_reservatorio = 12172'
    cotas = aux_collection_insert.consulta_BD(query)
    aux = list(cotas)
    list_of_cotas = []
    for value in aux:
        list_of_cotas.append(value[0])
    return list_of_cotas

def volumes():
    query = 'SELECT volume FROM tb_cav WHERE id_reservatorio = 12172'
    volumes = aux_collection_insert.consulta_BD(query)
    aux = list(volumes)
    list_of_volumes = []
    for value in aux:
        list_of_volumes.append(value[0])
    return list_of_volumes

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

def evap(mes):
    mes_dic = {'1' : 'jan', '2' : 'fev', '3' : 'mar', '4' : 'abr', '5' : 'mai', '6' : 'jun',
               '7' : 'jul', '8' : 'ago', '9' : 'set', '10' : 'out', '11' : 'nov', '12' : 'dez'}
    query = 'SELECT eva_' + mes_dic[str(mes)] + ' FROM tb_reservatorio WHERE id = 12172'
    evaporacao = aux_collection_insert.consulta_BD(query)[0][0]
    return evaporacao / 1000.0

def cota(vol):
    lv = volumes()
    lc = cotas()
    v_atual = float(vol)
    index = maisProximo(v_atual, lv)
    ct = ((lc[index+1] - lc[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + lc[index]
    print 'Cota: '+str(ct)
    return ct

def cotaEvap(mes, vol):
    lc = cotas()
    evaporacao = evap(mes)
    c_atual = cota(vol)
    c_final = lc[0]
    if (c_atual - evaporacao) >= lc[0]:
        c_final = c_atual - evaporacao
    print 'Cota Evap.: '+str(c_final)
    return c_final

def volumeParcial(mes, vol):
    lc = cotas()
    lv = volumes()
    c_final = cotaEvap(mes, vol)
    index = maisProximo(c_final, lc)
    vp = ((lv[index+1] - lv[index]) * ((c_final - lc[index]) / (lc[index+1] - lc[index]))) + lv[index]
    return vp

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

def demandas(today):
    mes = 1
    ano = int(today.year) - 1
    ld = []
    while mes <= 12:
        query_datas = """SELECT MIN(data_informacao), MAX(data_informacao) FROM tb_monitoramento WHERE id_reservatorio=12172 AND
                data_informacao BETWEEN '"""+str(ano)+"""-"""+str(mes)+"""-01' AND '"""+str(ano)+"""-"""+str(mes)+"""-31'"""
        rows_datas = rowsToList(aux_collection_insert.consulta_BD(query_datas))
        if len(rows_datas) > 0:
            if rows_datas[0] != rows_datas[1]:
                query_fim = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio=12172 AND data_informacao='"""+str(rows_datas[1])+"""'"""
                rows_fim = rowsToList(aux_collection_insert.consulta_BD(query_fim))

                query_inicio = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio=12172 AND data_informacao='"""+str(rows_datas[0])+"""'"""
                rows_inicio = rowsToList(aux_collection_insert.consulta_BD(query_inicio))

                dif_datas = rows_datas[1] - rows_datas[0]
                day = dif_datas.days
                vp2 = volumeParcial(rows_datas[0].month, float(rows_inicio[0]) * 1000000.00)
                vp1 = volumeParcial(rows_datas[1].month, float(rows_fim[0]) * 1000000.00)
                media_dem = (vp2 - vp1) / day

                print 'Mes: '+str(mes)
                print 'Datas / Volume: '+str(rows_datas[0])+' / '+str(rows_inicio[0])
                print 'Datas / Volume: '+str(rows_datas[1])+' / '+str(rows_fim[0])
                print 'Dif. Dias: '+str(day)
                print 'Volumes Parciais: '+str(vp2)+' / '+str(vp1)
                print 'Demanda Media: '+str(media_dem)
                print '---------'

                if media_dem > 0.0:
                    ld.append(media_dem)
        mes += 1

    demanda_res = sum(ld) / len(ld)
    query = """UPDATE tb_reservatorio SET demanda="""+str(demanda_res)+""" WHERE id=12172"""
    aux_collection_insert.update_BD(query)

today = date.today()
demandas(today)
