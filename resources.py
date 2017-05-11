#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, make_response, request, Response, json, redirect, url_for
import api_mandacaru
import StringIO
import csv
import os

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

@app.route('/api/reservatorios/<id>/monitoramento/csv')
def reservoirs_monitoring_csv(id):
	csvList = api_mandacaru.reservoirs_monitoring_csv(int(id))
	si = StringIO.StringIO()
	cw = csv.writer(si)
	cw.writerows(csvList)
	response = make_response(si.getvalue())
	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers["Content-Disposition"] = "attachment; filename=monitoramento_" + id + ".csv"
	response.headers["Content-type"] = "text/csv"
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

@app.route('/api/municipios/sab')
def city_info():
	response = json.dumps(api_mandacaru.city_info(1))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/municipios')
def city_info_brazil():
	response = json.dumps(api_mandacaru.city_info(0))
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/api/pesquisa/municipio_reservatorio')
def search_information():
	response = json.dumps(api_mandacaru.search_information())
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response

@app.route('/upload/verificacao',methods=['POST'])
def upload_file():
    response = json.dumps(api_mandacaru.verify_csv(request))
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response
