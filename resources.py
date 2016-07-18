#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask, make_response, request, Response
import json
import unicodedata
import api_mandacaru

app = Flask(__name__)


@app.route('/')
def api():
	return "Api do monitoramento dos reservatórios da região Semi-árida brasileira"

@app.route('/info_reservatorios/<id_reservatorio>')
def monitoramento_reservatorio(id_reservatorio):
	response = api_mandacaru.info_reservatorios(int(id_reservatorio))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/info_reservatorios')
def monitoramento_todos_reservatorios():
	response = api_mandacaru.info_reservatorios()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/regioes_brasil_topoJSON')
def regioes_brasil():
	response = api_mandacaru.regioes_brasil()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/cidades_sab')
def cidades_sab():
	response = api_mandacaru.cidades_sab()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/reservatorios_sab')
def reservatorios_sab():
	response = api_mandacaru.reservatorios_sab()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response