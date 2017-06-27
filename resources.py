#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, Response, json, make_response
import api_mandacaru
import StringIO
import csv
import sys, os
sys.path.append('../sab-api/script')
sys.path.append('../sab-api/authentication')
import aux_collection_insert
from hasher import digest, hash_all
from authorize import Authorize

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)

auth = Authorize("INSA")
completion = False

#Login
def get_response(status):
	data = {'Authorized' : status}
	response = json.dumps(data)
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Methods'] = "GET, POST, OPTIONS"
	response.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return response	
	
@app.route('/login', methods=['GET', 'POST', 'OPTIONS'])
def login():
	resp = get_response(completion)
	
	if session.get('logged_in') == auth.check_session() and session['logged_in'] != False:
		resp = get_response(completion)
		return resp
		
	if request.method == 'POST':
		json = request.json
		username = json.get("email")
		password = json.get("password")
        
		global completion
		completion = auth.authenticate(username, password)
        
		if completion == False:
			return resp
		else:
			session['logged_in'] = auth.gen_session(username)
			resp = get_response(completion)
			return resp
	
	elif request.method == 'OPTIONS':
		return resp 
	
	return resp
    
@app.route('/logout', methods=['GET', 'POST', 'OPTIONS'])
def logout():
    resp = get_response(completion)

    if request.method == 'POST':
        session['logged_in'] = False
        global completion
        completion = session['logged_in']
        resp = get_response(completion)
        return resp

    return resp

#Resources
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
	#response = json.dumps(api_mandacaru.reservoirs_monitoring_csv(int(id)))
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
