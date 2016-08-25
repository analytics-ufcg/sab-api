#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unicodedata import normalize
import math

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
			dicionario[keys[i]] = ajuste_acentos(values[i])
		else:
			dicionario[keys[i]] = values[i]
	return dicionario