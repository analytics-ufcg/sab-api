#!/usr/bin/env python
# -*- coding: utf-8 -*-

import predict_info

from datetime import timedelta, date, datetime

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

# - Retorno para o /previsões do reservatório.
# - Retorna previsões feitas a partir do último volume monitorado,
# retornando a previsão pela Outorga e pela Retirada (demanda), além do volume morto.
# - Condição: volume ser maior que ZERO e número de dias menor que 180 dias.
def compara(reservatId):
    data = predict_info.getDate(reservatId)

    volume_atual = predict_info.volumeAtual(reservatId)
    volume_morto = predict_info.volumeMorto(reservatId)

    volumesDemOut = calcula_previsoes(volume_atual, reservatId, data)

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

    volumesDemOut.append("%.4f" % round((volume_morto / 1000000.0), 4))
    return volumesDemOut

# - Função auxiliar para os cálculos de previsões
def calcula_previsoes(volume_atual, reservatId, data):
    predict_info.popular_variaveis(reservatId, data)

    volumesDemOut = [[], []]
    VOLUME_PARADA = 0.0

    outorga = predict_info.outorga(reservatId)
    demanda = predict_info.demanda(reservatId)

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
