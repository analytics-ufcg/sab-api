import aux_collection_insert

from datetime import timedelta, date, datetime

listaCotas = []
listaVolumes = []
evapDiv = 1

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

def evap(mes, reservatId):
    mes_dic = {'1' : 'jan', '2' : 'fev', '3' : 'mar', '4' : 'abr', '5' : 'mai', '6' : 'jun',
               '7' : 'jul', '8' : 'ago', '9' : 'set', '10' : 'out', '11' : 'nov', '12' : 'dez'}
    query = 'SELECT eva_' + mes_dic[str(mes)] + ' FROM tb_reservatorio WHERE id = '+str(reservatId)
    rows = aux_collection_insert.consulta_BD(query)
    evaporacao = rows[0][0] if len(rows) > 0 else 0.0
    return (evaporacao / 1000.0) / evapDiv if evaporacao != None else 0.0

def cota(vol, reservatId):
    lv = listaVolumes
    lc = listaCotas
    v_atual = float(vol)
    index = maisProximo(v_atual, lv)
    ct = ((lc[index+1] - lc[index]) * ((v_atual - lv[index]) / (lv[index+1] - lv[index]))) + lc[index]
    return ct

def cotaEvap(mes, vol, reservatId):
    lc = listaCotas
    evaporacao = evap(mes, reservatId)
    c_atual = cota(vol, reservatId)
    c_final = lc[0]
    if (c_atual - evaporacao) >= lc[0]:
        c_final = c_atual - evaporacao
    return c_final

def volumeParcial(mes, vol, reservatId):
    lc = listaCotas
    lv = listaVolumes
    c_final = cotaEvap(mes, vol, reservatId)
    index = maisProximo(c_final, lc)
    vp = ((lv[index+1] - lv[index]) * ((c_final - lc[index]) / (lc[index+1] - lc[index]))) + lv[index]
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

def demanda_opt(data, reservatId):
    mes_atual = int(data.month)
    mes_limite = int(data.month) - 6
    ano_atual = int(data.year)
    if mes_limite > 0:
        ano_limite = ano_atual
    else:
        ano_limite = ano_atual - 1
        mes_limite = 12 - mes_limite

    ld = []

    query = """SELECT data_informacao, volume FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
            data_informacao BETWEEN '"""+str(ano_limite)+"""-"""+str(mes_limite)+"""-01' AND '"""+str(ano_atual)+"""-"""+str(mes_atual)+"""-31' ORDER BY data_informacao ASC"""
    rows = rowsToList(aux_collection_insert.consulta_BD(query))

    if len(rows) > 0:
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

    demanda_res = sum(lista_dem) / len(lista_dem) if len(lista_dem) > 0 else 0.0
    print 'Demanda Total: '+str(demanda_res)
    query = """UPDATE tb_reservatorio SET demanda="""+str(demanda_res)+""" WHERE id="""+str(reservatId)
    aux_collection_insert.update_BD(query)


def demanda_atr(data, reservatId):
    mes = int(data.month) - 1
    ano = int(data.year)
    ld = []
    while len(ld) < 3:
        query_datas = """SELECT MIN(data_informacao), MAX(data_informacao) FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                data_informacao BETWEEN '"""+str(ano)+"""-"""+str(mes)+"""-01' AND '"""+str(ano)+"""-"""+str(mes)+"""-31'"""
        rows_datas = rowsToList(aux_collection_insert.consulta_BD(query_datas))

        print rows_datas

        if rows_datas[0] != None:
            query_fim = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                           data_informacao='"""+str(rows_datas[1])+"""'"""
            rows_fim = rowsToList(aux_collection_insert.consulta_BD(query_fim))

            query_inicio = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                              data_informacao='"""+str(rows_datas[0])+"""'"""
            rows_inicio = rowsToList(aux_collection_insert.consulta_BD(query_inicio))

            if float(rows_inicio[0]) > float(rows_fim[0]):
                dif_datas = rows_datas[1] - rows_datas[0]
                day = dif_datas.days
                vp2 = volumeParcial(rows_datas[0].month, float(rows_inicio[0]) * 1000000.00, reservatId)
                vp1 = volumeParcial(rows_datas[1].month, float(rows_fim[0]) * 1000000.00, reservatId)
                media_dem = (vp2 - vp1) / day
                ld.append(media_dem)

                print 'Mes: '+str(mes)
                print 'Datas / Volume: '+str(rows_datas[0])+' / '+str(rows_inicio[0])
                print 'Datas / Volume: '+str(rows_datas[1])+' / '+str(rows_fim[0])
                print 'Dif. Dias: '+str(day)
                print 'Volumes Parciais: '+str(vp2)+' / '+str(vp1)
                print 'Demanda Media: '+str(media_dem)
                print '---------'

        mes -= 1
        if mes == 0:
            ano -= 1
            mes = 12

    demanda_res = sum(ld) / len(ld) if len(ld) > 0 else 0.0
    print 'Demanda Total: '+str(demanda_res)
    query = """UPDATE tb_reservatorio SET demanda="""+str(demanda_res)+""" WHERE id="""+str(reservatId)
    aux_collection_insert.update_BD(query)

def demandas(data, reservatId):
    mes = 1
    ano = int(data.year) - 1
    ld = []
    while mes <= 12:
        query_datas = """SELECT MIN(data_informacao), MAX(data_informacao) FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                data_informacao BETWEEN '"""+str(ano)+"""-"""+str(mes)+"""-01' AND '"""+str(ano)+"""-"""+str(mes)+"""-31'"""
        rows_datas = rowsToList(aux_collection_insert.consulta_BD(query_datas))
        if len(rows_datas) > 0:
            if rows_datas[0] != rows_datas[1]:
                query_fim = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                               data_informacao='"""+str(rows_datas[1])+"""'"""
                rows_fim = rowsToList(aux_collection_insert.consulta_BD(query_fim))

                query_inicio = """SELECT volume, data_informacao FROM tb_monitoramento WHERE id_reservatorio="""+str(reservatId)+""" AND
                                  data_informacao='"""+str(rows_datas[0])+"""'"""
                rows_inicio = rowsToList(aux_collection_insert.consulta_BD(query_inicio))

                dif_datas = rows_datas[1] - rows_datas[0]
                day = dif_datas.days
                vp2 = volumeParcial(rows_datas[0].month, float(rows_inicio[0]) * 1000000.00, reservatId)
                vp1 = volumeParcial(rows_datas[1].month, float(rows_fim[0]) * 1000000.00, reservatId)
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

    demanda_res = sum(ld) / len(ld) if len(ld) > 0 else 0.0
    print 'Demanda Total: '+str(demanda_res)
    query = """UPDATE tb_reservatorio SET demanda="""+str(demanda_res)+""" WHERE id="""+str(reservatId)
    aux_collection_insert.update_BD(query)

def ids_PB():
    query = """SELECT DISTINCT res.id
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
               ORDER BY res.id ASC"""
    rows = rowsToList(aux_collection_insert.consulta_BD(query))
    return rows

def create_demanda():
    query = """ALTER TABLE tb_reservatorio ADD COLUMN demada VARCHAR(45) NULL AFTER longitude"""
    aux_collection_insert.update_BD(query)

def popular_demanda():
    global listaCotas
    listaCotas = cotas(reservatId)
    global listaVolumes
    listaVolumes = volumes(reservatId)

    today = date.today()
    ids_list = ids_PB()
    for reservatId in ids_list:
        demanda_opt(today, reservatId)
