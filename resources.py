#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask, make_response, request, Response, json
import api_mandacaru

app = Flask(__name__)


@app.route('/api')
def api():
	return "Api do monitoramento dos reservatórios da região Semi-árida brasileira"

@app.route('/api/estados/sab')
def states_sab():
	response = json.dumps(api_mandacaru.states_sab())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/pais')
def json_brazil():
	response = json.dumps(api_mandacaru.json_brazil())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios')
def reservoirs():
	response = json.dumps(api_mandacaru.reservoirs())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/info')
@app.route('/api/reservatorios/<id>/info')
def reservoirs_information(id=None):
	if (id is None):
		response = json.dumps(api_mandacaru.reservoirs_information())
	else:
		response = json.dumps(api_mandacaru.reservoirs_information(int(id)))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/<id>/monitoramento')
def reservoirs_monitoring(id):
	response = json.dumps(api_mandacaru.reservoirs_monitoring(int(id),False))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/<id>/monitoramento/completo')
def reservoirs_monitoring_complete(id):
	response = json.dumps(api_mandacaru.reservoirs_monitoring(int(id),True))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/reservatorios/similares/<nome>/<limiar>')
def reservoirs_similar(nome, limiar):
	response = json.dumps(api_mandacaru.reservoirs_similar(nome, int(limiar)))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response


@app.route('/api/reservatorio/equivalente/bacia')
def reservoirs_equivalent_hydrographic_basin():
	response = json.dumps(api_mandacaru.reservoirs_equivalent_hydrographic_basin())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response


@app.route('/api/reservatorio/equivalente/estado')
def reservoirs_equivalent_states():
	response = json.dumps(api_mandacaru.reservoirs_equivalent_states())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response
