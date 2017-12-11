#!/usr/bin/env python
# -*- coding: utf-8 -*-

import predict_info

from datetime import timedelta, date, datetime

def mae(reservatId, data):
    response = []

    vol_reais = getVolumes("real", reservatId, data)
    vol_pred = getVolumes("retirada", reservatId, data)
    result_fit = fitVolumes(vol_reais, vol_pred)
    fit = result_fit[1]
    difs = difference(vol_reais, fit)

    error = sum(difs)/len(difs) if len(difs) > 0 else None
    response.append(error)
    response.append(result_fit[0])
    return response

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
    print data_final

    if tipo == "real":
        rows = rowsToList(predict_info.volumesEntre(reservatId, data_inicial, data_final))

    elif tipo == "retirada":
        volume_atual = predict_info.volumePassado(reservatId, data_inicial)
        predict_info.popular_variaveis(reservatId, data_inicial)

        VOLUME_PARADA = 0.0

        demanda = predict_info.demanda(data_inicial, reservatId)

        if demanda != None:
            dias = 0
            va_dem = volume_atual
            while (va_dem > VOLUME_PARADA and dias < 180):
                previsao = predict_info.volumeParcial(reservatId, data_inicial, va_dem) + predict_info.precip() + predict_info.vazao() - demanda
                va_dem = previsao if previsao > 0.0 else 0.0
                rows.append("%.4f" % round((va_dem / 1000000.0), 4))
                dias = dias + 1
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
