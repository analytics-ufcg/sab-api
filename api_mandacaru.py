#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from unicodedata import normalize
import IOFiles

def info_reservatorios(id_reservatorio=None):
	reservatorios_detalhes = IOFiles.reservatorios_detalhes()

	if(id_reservatorio is None):
		return(json.dumps(reservatorios_detalhes))
	else:
		for reserv in reservatorios_detalhes:
			if (id_reservatorio == reserv["GEOCODIGO"]):
				return(json.dumps(reserv))


def monitoramento_reservatorios(id):
	monitoramento = IOFiles.monitoramento()
	try :
		return(json.dumps({'volumes': monitoramento[id]}))
	except :
		return(json.dumps({'volumes': []}))


def estados_br():
	return(json.dumps(IOFiles.estados_br()))

def estados_sab():
	return(json.dumps(IOFiles.estados_sab()))

def reservatorios():
	return(json.dumps(IOFiles.reservatorios()))

def municipios_sab():
	return(json.dumps(IOFiles.municipios_sab()))

def remover_acentos(txt):
	return normalize('NFKD', txt).encode('ASCII','ignore').decode('ASCII')

def remover_espacos(txt):
	return txt.replace(" ", "")
