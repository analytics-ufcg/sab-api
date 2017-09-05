#!/usr/bin/env python
# -*- coding: utf-8 -*-

import predict_info

from datetime import timedelta, date, datetime

def calcula(dictionary):
    reservatId = dictionary["id"]

    volume_atual = float(dictionary["volume"]) * 1000000.00

    ultima_data = dictionary["data_informacao"]
    ultima_data = datetime.strptime(ultima_data, "%d/%m/%Y").date()
    data = date.today()
    dif_datas = data - ultima_data

    predict_info.popular_variaveis(reservatId, data)
    dias = 0

    dem = predict_info.demanda(reservatId)
    volume_morto = predict_info.volumeMorto(reservatId)

    if dif_datas.days <= 7 and dem != None:
        while (volume_atual > volume_morto):
            previsao = predict_info.volumeParcial(reservatId, data, volume_atual) + predict_info.precip() + predict_info.vazao() - dem
            volume_atual = previsao
            dias += 1
            data += timedelta(days=1)
        return dias
    else:
        return None

def compara(reservatId):
    volumesDemOut = [[], []]

    data = date.today()

    predict_info.popular_variaveis(reservatId, data)

    outorga = predict_info.outorga(reservatId)
    demanda = predict_info.demanda(reservatId)

    volume_atual = predict_info.volumeAtual(reservatId)
    volume_morto = predict_info.volumeMorto(reservatId)

    if demanda != None:
        va_dem = volume_atual
        while (va_dem > volume_morto):
            previsao = predict_info.volumeParcial(reservatId, data, va_dem) + predict_info.precip() + predict_info.vazao() - demanda
            va_dem = previsao
            volumesDemOut[0].append("%.2f" % round((va_dem / 1000000.0), 2))
    else:
        volumesDemOut[0] = None

    if outorga != None and len(predict_info.cotas(reservatId)):
        va_outorga = volume_atual
        while (va_outorga > volume_morto):
            previsao = predict_info.volumeParcial(reservatId, data, va_outorga) + predict_info.precip() + predict_info.vazao() - outorga
            va_outorga = previsao
            volumesDemOut[1].append("%.2f" % round((va_outorga / 1000000.0), 2))
    else:
        volumesDemOut[1] = None

    volumesDemOut.append("%.2f" % round((volume_morto / 1000000.0), 2))
    return volumesDemOut
