#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unicodedata import normalize
import math
from dateutil import relativedelta
from datetime import datetime

def remover_acentos(txt):
	if (type(txt) is str):
		txt= unicode(txt, "utf-8")
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def ajuste_acentos(txt):
	return unicode(txt, 'unicode-escape')

def lista_dicionarios(list_of_values, keys):
	lista_resposta = []
	for valor in list_of_values:
		lista_resposta.append(cria_dicionario(valor,keys))
	return lista_resposta

def cria_dicionario(values, keys):
	dicionario = {}
	for i in range(len(values)):
		if (type(values[i]) is str):
			dicionario[keys[i]] = values[i]
		else:
			dicionario[keys[i]] = values[i]
	return dicionario

def ajuste_dados_com_intervalo(monitoramento):
	result = []
	diasRange = relativedelta.relativedelta(days=60)
	dia = relativedelta.relativedelta(days=1)
	for m in range(len(monitoramento)-1):
		result.append(monitoramento[m])
		if(datetime.strptime(monitoramento[m][1], "%d/%m/%Y") <= (datetime.strptime(monitoramento[m+1][1], "%d/%m/%Y")- diasRange)):
			dataVaziaInicial = (datetime.strptime(monitoramento[m][1], "%d/%m/%Y")+dia).strftime("%d/%m/%Y")
			dataVaziaFinal = (datetime.strptime(monitoramento[m+1][1], "%d/%m/%Y")-dia).strftime("%d/%m/%Y")
			result.append((None,monitoramento[m][1],None))
			result.append((None,monitoramento[m+1][1],None))
	result.append(monitoramento[len(monitoramento)-1])


	return result