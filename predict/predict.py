import info
from datetime import datetime, timedelta

def calcula(reservatId):
    today = datetime.date.today()
    lastWeek = today - timedelta(days=7)
    mes = data.month

    info.popular_variaveis(reservatId)

    previsao = info.volumeParcial(reservatId, mes) + info.precip() + \
    info.vazao() - info.evap(reservatId, mes) - info.demanda(reservatId, lastWeek)
    return previsao
