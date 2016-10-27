#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask, make_response, request, Response, json
import api_mandacaru

app = Flask(__name__)


@app.route('/api')
def api():
	return "Api do monitoramento dos reservatórios da região Semi-árida brasileira"

# @app.route('/api/estados/br')
# def estados_br():
# 	response = api_mandacaru.estados_br()
# 	response = make_response(response)
# 	response.headers['Access-Control-Allow-Origin'] = "*"
# 	return response

@app.route('/api/estados/sab')
def estados_sab():
	response = json.dumps(api_mandacaru.estados_sab())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

# @app.route('/api/municipios/sab')
# def municipios_sab():
# 	response = api_mandacaru.municipios_sab()
# 	response = make_response(response)
# 	response.headers['Access-Control-Allow-Origin'] = "*"
# 	return response

@app.route('/api/reservatorios')
def reservatorios():
	response = json.dumps(api_mandacaru.reservatorios())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/info')
@app.route('/api/reservatorios/<id>/info')
def info_reservatorios(id=None):
	if (id is None):
		response = json.dumps(api_mandacaru.info_reservatorios_BD())
	else:
		response = json.dumps(api_mandacaru.info_reservatorios_BD(int(id)))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/<id>/monitoramento')
def monitoramento_reservatorios(id):
	response = json.dumps(api_mandacaru.monitoramento_reservatorios_BD(int(id),False))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/<id>/monitoramento/completo')
def monitoramento_reservatorios_completo(id):
	response = json.dumps(api_mandacaru.monitoramento_reservatorios_BD(int(id),True))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response


@app.route('/api/reservatorios/similares/<nome>')
def similares_reservatorios(nome):
	response = json.dumps(api_mandacaru.similares_reservatorios(nome))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response


@app.route('/api/reservatorio/equivalente/bacia')
def reservatorio_equivalente_bacia():
	response = json.dumps(api_mandacaru.reservatorio_equivalente_bacia())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response


@app.route('/api/reservatorio/equivalente/estado')
def reservatorio_equivalente_estado():
	response = json.dumps(api_mandacaru.reservatorio_equivalente_estado())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response
