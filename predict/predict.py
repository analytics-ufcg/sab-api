import predict_info
import aux_predict_info

from datetime import timedelta, date, datetime

def calcula(list_of_values):
    reservatId = list_of_values[0]

    volume_atual = float(list_of_values[10]) * 1000000.00

    #data = list_of_values[12]
    #data = datetime.strptime(data, "%d/%m/%Y").date()

    data = date.today()

    predict_info.popular_variaveis(reservatId)
    dias = 0

    dem = predict_info.demanda(reservatId)
    volume_morto = 28238900.00

    while (volume_atual > volume_morto):
        previsao = predict_info.volumeParcial(reservatId, data, volume_atual) + predict_info.precip() + predict_info.vazao() - dem
        volume_atual = previsao
        dias += 1
        data += timedelta(days=1)

    return dias
