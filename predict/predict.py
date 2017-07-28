import predict_info

from datetime import timedelta, date, datetime

def calcula(list_of_values):
    reservatId = list_of_values[0]
    vol = list_of_values[10]
    data = list_of_values[12]
    data = datetime.strptime(data, "%d/%m/%Y").date()
    mes = data.month

    predict_info.popular_variaveis(reservatId)

    previsao = predict_info.volumeParcial(reservatId, mes, vol) + predict_info.precip() + predict_info.vazao() \
                - predict_info.evap(reservatId, vol) - predict_info.demanda(reservatId, data, vol)

    return previsao
