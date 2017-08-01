import predict_info
import aux_predict_info

from datetime import timedelta, date, datetime

def calcula(list_of_values):
    reservatId = list_of_values[0]

    volume_atual = float(list_of_values[10]) * 1000000.00
    volume_critico = aux_predict_info.critical(reservatId)

    data = list_of_values[12]
    data = datetime.strptime(data, "%d/%m/%Y").date()
    mes = data.month

    predict_info.popular_variaveis(reservatId)
    dias = 0

    while (volume_atual > volume_critico):
        print volume_atual
        previsao = predict_info.volumeParcial(reservatId, mes, volume_atual) + predict_info.precip() + predict_info.vazao() \
                    - predict_info.evap(reservatId, mes) - predict_info.demanda(reservatId, data, volume_atual)
        volume_atual = previsao
        dias += 1

    print volume_critico
    return dias
