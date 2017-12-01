#!/usr/bin/env python
# -*- coding: utf-8 -*-

import predict_info
import precisao

from datetime import timedelta, date, datetime
from pandas import Series
from statsmodels.tsa.arima_model import ARIMA
import numpy

#Retorno para o /info do reservatório.
#Adiciona uma previsão do números de dias restantes de água.
#Condição: último dado de volume ser mais novo do que 7 dias e o reservatório possuir informação de demanda.
def calcula(dictionary):
    reservatId = dictionary["id"]

    volume_atual = float(dictionary["volume"]) * 1000000.00

    ultima_data = dictionary["data_informacao"]
    ultima_data = datetime.strptime(ultima_data, "%d/%m/%Y").date()
    data = date.today()
    dif_datas = data - ultima_data

    predict_info.popular_variaveis(reservatId, data)
    dias = 0

    dem = predict_info.demanda(data, reservatId)
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

# - Retorno para o /previsões do reservatório.
# - Retorna previsões feitas a partir do último volume monitorado,
# retornando a previsão pela Outorga e pela Retirada (demanda), além do volume morto.
# - Condição: volume ser maior que ZERO e número de dias menor que 180 dias.
def compara(reservatId):
    data = predict_info.getDate(reservatId)

    volume_atual = predict_info.volumeAtual(reservatId)
    volume_morto = predict_info.volumeMorto(reservatId)

    volumesDemOut = calcula_previsoes(volume_atual, reservatId, data)
    volumeMat = previsao_matematica(reservatId, data)

    volumesDemOut.append(volumeMat)
    volumesDemOut.append("%.4f" % round((volume_morto / 1000000.0), 4))
    return volumesDemOut

# - Retorno para o /previsões do reservatório.
# - Retorna previsões feitas a partir do último volume monitorado,
# retornando a previsão pela Outorga e pela Retirada (demanda), além do volume morto.
# - Condição: volume ser maior que ZERO e número de dias menor que 180 dias.
def compara_passado(reservatId, ultimaData):
    data = datetime.strptime(ultimaData, "%Y-%m-%d").date()

    volume_atual = predict_info.volumePassado(reservatId, ultimaData)
    volume_morto = predict_info.volumeMorto(reservatId)

    volumesDemOut = calcula_previsoes(volume_atual, reservatId, data)
    volumeMat = previsao_matematica(reservatId, ultimaData)

    volumesDemOut.append(volumeMat)
    volumesDemOut.append("%.4f" % round((volume_morto / 1000000.0), 4))
    return volumesDemOut

# - Função auxiliar para os cálculos de previsão por modelo matemático
def previsao_matematica(reservatId, data):
    seriesArray = Series.from_array(predict_info.getSeries(reservatId, data))
    seriesValues = seriesArray.values

    mathDict = {'calculado': False, 'volumes': [], 'dias': 0}

    # seasonal difference
    days_in_year = 1
    differenced = predict_info.difference(seriesValues, days_in_year)
    # fit model
    model = ARIMA(differenced, order=(1,0,1))
    model_fit = model.fit(disp=0)
    # multi-step out-of-sample forecast
    forecast = model_fit.forecast(steps=180)[0]
    # invert the differenced forecast to something usable
    mathDict['calculado'] = True
    history = [x for x in seriesValues]
    for yhat in forecast:
    	inverted = predict_info.inverse_difference(history, yhat, days_in_year)
        history.append(inverted)
        if inverted >= 0.0:
            mathDict['volumes'].append("%.4f" % round((inverted), 4))
            mathDict['dias'] = mathDict['dias'] + 1
    return mathDict

# - Função auxiliar para os cálculos de previsões
def calcula_previsoes(volume_atual, reservatId, data):
    predict_info.popular_variaveis(reservatId, data)

    volumesDemOut = [[], []]
    VOLUME_PARADA = 0.0

    outorga = predict_info.outorga(reservatId)
    demanda = predict_info.demanda(data, reservatId)

    outorgasDict = {'calculado': False, 'volumes': [], 'dias': 0}
    previsaoDict = {'calculado': False, 'volumes': [], 'dias': 0}

    if demanda != None:
        va_dem = volume_atual
        previsaoDict['calculado'] = True
        while (va_dem > VOLUME_PARADA and previsaoDict['dias'] < 180):
            previsao = predict_info.volumeParcial(reservatId, data, va_dem) + predict_info.precip() + predict_info.vazao() - demanda
            va_dem = previsao if previsao > 0.0 else 0.0
            previsaoDict['volumes'].append("%.4f" % round((va_dem / 1000000.0), 4))
            previsaoDict['dias'] = previsaoDict['dias'] + 1
        volumesDemOut[0] = previsaoDict
    else:
        volumesDemOut[0] = previsaoDict

    if outorga != None and len(predict_info.cotas(reservatId)):
        va_outorga = volume_atual
        outorgasDict['calculado'] = True
        while (va_outorga > VOLUME_PARADA and outorgasDict['dias'] < 180):
            previsao = predict_info.volumeParcial(reservatId, data, va_outorga) + predict_info.precip() + predict_info.vazao() - outorga
            va_outorga = previsao if previsao > 0.0 else 0.0
            outorgasDict['volumes'].append("%.4f" % round((va_outorga / 1000000.0), 4))
            outorgasDict['dias'] = outorgasDict['dias'] + 1
        volumesDemOut[1] = outorgasDict
    else:
        volumesDemOut[1] = outorgasDict

    return volumesDemOut

def porcentagem(reservatId, volume):
    vol = float(volume)
    cap = float(predict_info.getCapacidade(reservatId))
    nivel = round((vol*100.00)/cap, 4)
    return nivel
