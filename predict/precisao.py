#!/usr/bin/env python
# -*- coding: utf-8 -*-

import predict_info
import predict

from datetime import timedelta, date, datetime

response = []

def mae(reservatId, data):
    global response
    response = []

    vol_reais = getVolumes("real", reservatId, data)
    previsoes = predict.compara_passado(reservatId, data)
    vol_retiradas = previsoes[0]["volumes"]
    vol_outorgas = previsoes[1]["volumes"]
    vol_modelo = previsoes[2]["volumes"]

    #Retirada
    result_fit_ret = fitVolumes(vol_reais, vol_retiradas)
    calculateError(vol_reais, result_fit_ret)
    #Outorga
    result_fit_out = fitVolumes(vol_reais, vol_outorgas)
    calculateError(vol_reais, result_fit_out)
    #Modelo Matemático
    result_fit_mod = fitVolumes(vol_reais, vol_modelo)
    calculateError(vol_reais, result_fit_mod)

    return response

def calculateError(vol_reais, result_fit):
    fit = result_fit[1]
    difs = difference(vol_reais, fit)
    error = sum(difs)/len(difs) if len(difs) > 0 else None
    global response
    response.append(error)
    global response
    response.append(result_fit[0])

def difference(reais, fit):
    difs = []
    index = 3
    for i in range(0, len(fit), 1):
        yi = fit[i]
        xi = reais[index]
        index = index + 2
        dif = abs(float(yi) - float(xi))
        difs.append(dif)
    return difs

def fitVolumes(reais, pred):
    result = ["", []]
    fit = []
    index = -1
    for i in range(0, len(reais)-3, 2):
        data_inicial = datetime.strptime(reais[i], "%Y-%m-%d").date()
        data_final = datetime.strptime(reais[i+2], "%Y-%m-%d").date()
        dif_datas = data_final - data_inicial
        dias = dif_datas.days

        index = index + dias - 1
        if index < len(pred):
            fit.append(pred[index])
            result[0] = data_final
            result[1] = fit
        else:
            return result
    return result

def getVolumes(tipo, reservatId, data):
    rows = []
    data_inicial = datetime.strptime(data, "%Y-%m-%d").date()
    data_final = data_inicial + timedelta(days=180)

    print "-----------------------------------------------"
    print data_inicial
    print data_final

    rows = rowsToList(predict_info.volumesEntre(reservatId, data_inicial, data_final))

    return rows

def rowsToList(rows):
    lista = []
    lista_externa = list(rows)
    if len(lista_externa) > 0:
        for li in lista_externa:
            aux = list(li)
            if len(aux) > 1:
                lista.append(str(aux[0]))
                lista.append(aux[1])
            else:
                lista.append(aux[0])
        return lista
    else:
        return lista
