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

@app.route('/estados/br')
def estados_br():
	response = api_mandacaru.estados_br()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/estados/sab')
def estados_sab():
	response = api_mandacaru.estados_sab()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/reservatorios')
def reservatorios():
	response = api_mandacaru.reservatorios()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/reservatorios/<id>/info')
def monitoramento_reservatorio(id):
	response = api_mandacaru.info_reservatorios(int(id))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/reservatorios/info')
def monitoramento_todos_reservatorios():
	response = api_mandacaru.info_reservatorios()
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response
