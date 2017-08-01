import predict_info
import aux_predict_info

from datetime import timedelta, date, datetime

def calcula(list_of_values):
    reservatId = list_of_values[0]

    volume_atual = float(list_of_values[10]) * 1000000.00

    data = list_of_values[12]
    data = datetime.strptime(data, "%d/%m/%Y").date()
    mes = data.month

    predict_info.popular_variaveis(reservatId)
    dias = 0

    demanda = predict_info.demanda(reservatId, data, volume_atual)

    while (volume_atual > 0.0):
        previsao = predict_info.volumeParcial(reservatId, mes, volume_atual) + predict_info.precip() + predict_info.vazao() - demanda
        volume_atual = previsao
        dias += 1

    return dias
