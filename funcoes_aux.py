#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unicodedata import normalize
import math
from dateutil import relativedelta
from datetime import datetime
from fuzzywuzzy import fuzz
import re
from scipy import stats



def remover_acentos(txt):
	if (type(txt) is str):
		txt= unicode(txt, "utf-8")
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def ajuste_acentos(txt):
	return unicode(txt, 'unicode-escape')

def lista_dicionarios(list_of_values, keys, especial=None):
	lista_resposta = []
	for valor in list_of_values:
		dicionario = cria_dicionario(valor,keys)
		if (especial == "info"):
			dicionario["nome_sem_acento"] = remover_acentos(dicionario["nome"])
			dicionario["reservat_sem_acento"] = remover_acentos(dicionario["reservat"])
		lista_resposta.append(dicionario)
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
	diasRange = relativedelta.relativedelta(days=90)
	dia = relativedelta.relativedelta(days=1)
	for m in range(len(monitoramento)-1):
		result.append(monitoramento[m])
		if(datetime.strptime(monitoramento[m][1], "%d/%m/%Y") <= (datetime.strptime(monitoramento[m+1][1], "%d/%m/%Y")- diasRange)):
			dataVaziaInicial = (datetime.strptime(monitoramento[m][1], "%d/%m/%Y")+dia).strftime("%d/%m/%Y")
			dataVaziaFinal = (datetime.strptime(monitoramento[m+1][1], "%d/%m/%Y")-dia).strftime("%d/%m/%Y")
			result.append((None,monitoramento[m][1],None))
			result.append((None,monitoramento[m+1][1],None))
	if(len(monitoramento) > 0):
		result.append(monitoramento[len(monitoramento)-1])


	return result

def reservatorios_similares(nome_reservatorio, reservatorios):
	lista_reservatorios = []

	for reserv in reservatorios:
		reserv["apelido"] = re.sub(remover_acentos(reserv["nome"])+'|acude|barragem|lagoa|[()-]| do | da | de ','',remover_acentos(reserv["reservat"]), flags=re.IGNORECASE).strip()
		semelhanca_reservat = fuzz.token_set_ratio(remover_acentos(nome_reservatorio),remover_acentos(reserv["reservat"]))
		semelhanca_nome = fuzz.token_set_ratio(remover_acentos(nome_reservatorio),remover_acentos(reserv["nome"]))
		semelhanca_apelido = fuzz.token_set_ratio(remover_acentos(nome_reservatorio),remover_acentos(reserv["apelido"]))

		reserv["semelhanca"] = max(semelhanca_reservat,semelhanca_nome,semelhanca_apelido)

		lista_reservatorios.append(reserv)

	# Pega os 5 mais semelhantes
	lista_reservatorios_ordenada = sorted(lista_reservatorios, key=lambda k: k['semelhanca'], reverse=True)

	# Filtra os 100% semelhantes
	lista_reservatorios_filtrada = list(filter(lambda d: d['semelhanca'] == 100, lista_reservatorios_ordenada))

	# Se não tiver nenhum 100% semelhante retorna os 5 primeiros, caso contrário os semelhantes
	if(len(lista_reservatorios_filtrada) == 0):
		return lista_reservatorios_ordenada[:5]
	else:
		return lista_reservatorios_filtrada[:10]

def gradiente_regressao(lista1,lista2):
	gradient, intercept, r_value, p_value, std_err = stats.linregress(lista1,lista2)
	return gradient
