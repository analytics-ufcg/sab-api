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

    if dif_datas.days <= 7 and dem != "NULL":
        while (volume_atual > volume_morto):
            previsao = predict_info.volumeParcial(reservatId, data, volume_atual) + predict_info.precip() + predict_info.vazao() - dem
            volume_atual = previsao
            dias += 1
            data += timedelta(days=1)
        return dias
    else:
        return None
