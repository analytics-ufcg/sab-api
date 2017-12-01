#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, Response, json, make_response
from flask_jwt_extended import JWTManager, jwt_required, \
    get_jwt_identity, revoke_token, unrevoke_token, \
    get_stored_tokens, get_all_stored_tokens, create_access_token, \
    create_refresh_token, jwt_refresh_token_required, \
    get_raw_jwt, get_stored_token

import simplekv.memory
import datetime
import api_mandacaru
import funcoes_aux
import StringIO
import csv
import sys, os
sys.path.append('../sab-api/script')
sys.path.append('../sab-api/authentication')
sys.path.append('../sab-api/predict')

import aux_collection_insert
import predict
import precisao
from hasher import digest, hash_all
from authorize import Authorize

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_STORE'] = simplekv.memory.DictStore()
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = 'all'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=5)

jwt = JWTManager(app)

auth = Authorize("INSA")
completion = False

#CORS headers
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With')
    return response

#Authentication
def get_response(data):
	response = make_response(data)
	response.headers['Access-Control-Allow-Methods'] = "GET, POST, OPTIONS"
	return response

@app.route('/login', methods=['POST'])
def login():
    data = jsonify({'Authorized' : completion})
    resp = get_response(data)

    if request.method == 'POST':
        json = request.json
        username = json.get("email")
        password = json.get("password")

        global completion
        completion = auth.authenticate(username, password)

        if completion == False:
            data = jsonify({'Authorized' : completion, "msg": "Bad username or password"})
            return get_response(data), 401

        data = jsonify({
            'Authorized' : completion,
            'access_token' : create_access_token(identity=username),
            'refresh_token' : create_refresh_token(identity=username)
        })
        return get_response(data), 200

    return resp

@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200

def _revoke_current_token():
    current_token = get_raw_jwt()
    jti = current_token['jti']
    revoke_token(jti)

@app.route('/logout', methods=['POST'])
@jwt_required
def logout():
    data = jsonify({'Authorized' : completion})
    resp = get_response(data)

    if request.method == 'POST':
        try:
            _revoke_current_token()
            global completion
            completion = False
        except KeyError:
            return jsonify({
                'msg': 'Access token not found in the blacklist store'
            }), 500

        data = jsonify({'Authorized' : completion, "msg": "Logged Out"})
        return get_response(data), 200

    return resp

#Resources
@app.route('/api')
def api():
	return "Api do monitoramento dos reservatórios da região Semi-árida brasileira"

@app.route('/api/estados/sab')
def states_sab():
	response = json.dumps(api_mandacaru.states_sab())
	response = make_response(response)
	return response

@app.route('/api/pais')
def json_brazil():
	response = json.dumps(api_mandacaru.json_brazil())
	response = make_response(response)
	return response

@app.route('/api/reservatorios')
def reservoirs():
	response = json.dumps(api_mandacaru.reservoirs())
	response = make_response(response)
	return response

@app.route('/api/reservatorios/info')
@app.route('/api/reservatorios/<id>/info')
def reservoirs_information(id=None):
    if (id is None):
        response = json.dumps(api_mandacaru.reservoirs_information())
    else:
        response = json.dumps(api_mandacaru.reservoirs_information(int(id)))
	response = make_response(response)
    return response

@app.route('/api/reservatorios/<id>/monitoramento')
def reservoirs_monitoring(id):
	response = json.dumps(api_mandacaru.reservoirs_monitoring(int(id),False))
	response = make_response(response)
	return response

@app.route('/api/reservatorios/<id>/monitoramento/csv')
def reservoirs_monitoring_csv(id):
	csvList = api_mandacaru.reservoirs_monitoring_csv(int(id))
	si = StringIO.StringIO()
	cw = csv.writer(si)
	cw.writerows(csvList)
	response = make_response(si.getvalue())
	response.headers["Content-Disposition"] = "attachment; filename=monitoramento_" + id + ".csv"
	response.headers["Content-type"] = "text/csv"
	return response

@app.route('/api/reservatorios/<id>/monitoramento/completo')
def reservoirs_monitoring_complete(id):
	response = json.dumps(api_mandacaru.reservoirs_monitoring(int(id),True))
	response = make_response(response)
	return response

@app.route('/api/reservatorios/similares/<nome>/<limiar>')
def reservoirs_similar(nome, limiar):
	response = json.dumps(api_mandacaru.reservoirs_similar(nome, int(limiar)))
	response = make_response(response)
	return response


@app.route('/api/reservatorio/equivalente/bacia')
def reservoirs_equivalent_hydrographic_basin():
	response = json.dumps(api_mandacaru.reservoirs_equivalent_hydrographic_basin())
	response = make_response(response)
	return response


@app.route('/api/reservatorio/equivalente/estado')
def reservoirs_equivalent_states():
	response = json.dumps(api_mandacaru.reservoirs_equivalent_states())
	response = make_response(response)
	return response

@app.route('/api/municipios/sab')
def city_info():
	response = json.dumps(api_mandacaru.city_info(1))
	response = make_response(response)
	return response

@app.route('/api/municipios')
def city_info_brazil():
	response = json.dumps(api_mandacaru.city_info(0))
	response = make_response(response)
	return response

@app.route('/api/pesquisa/municipio_reservatorio')
def search_information():
	response = json.dumps(api_mandacaru.search_information())
	response = make_response(response)
	return response

@jwt_required
@app.route('/api/upload/verificacao',methods=['POST'])
def upload_file():
    response = json.dumps(api_mandacaru.verify_csv(request))
    response = make_response(response)
    return response

@jwt_required
@app.route('/api/upload/confirmacao/<id>',methods=['GET','POST'])
def confirm_upload(id=None):
	response = json.dumps(api_mandacaru.confirm_upload(request,id))
	response = make_response(response)
	return response

@app.route('/api/reservatorios/<id>/previsoes')
@app.route('/api/reservatorios/<id>/<date>/previsoes')
def pred(id=None, date=None):
    if date == None:
        listaPrevisoes = predict.compara(id)
        date = funcoes_aux.get_last_date(id)
    else:
        listaPrevisoes = predict.compara_passado(id, date)
        date = datetime.datetime.strptime(date,'%Y-%m-%d')

    days_previsao = [(date+datetime.timedelta(days=i)).strftime('%d/%m/%Y') for i in range(1,1+len(listaPrevisoes[0]['volumes']))]
    days_outorga = [(date+datetime.timedelta(days=i)).strftime('%d/%m/%Y') for i in range(1,1+len(listaPrevisoes[1]['volumes']))]
    days_math = [(date+datetime.timedelta(days=i)).strftime('%d/%m/%Y') for i in range(1,1+len(listaPrevisoes[2]['volumes']))]

    listaPrevisoes[0]['volumes'] = [{"DataInformacao" : days_previsao[i], "Volume" : listaPrevisoes[0]['volumes'][i], "Porcentagem" : predict.porcentagem(id, listaPrevisoes[0]['volumes'][i])} for i in range(len(listaPrevisoes[0]['volumes']))]
    listaPrevisoes[1]['volumes'] = [{"DataInformacao" : days_outorga[i], "Volume" : listaPrevisoes[1]['volumes'][i], "Porcentagem" : predict.porcentagem(id, listaPrevisoes[1]['volumes'][i])} for i in range(len(listaPrevisoes[1]['volumes']))]
    listaPrevisoes[2]['volumes'] = [{"DataInformacao" : days_math[i], "Volume" : listaPrevisoes[2]['volumes'][i], "Porcentagem" : predict.porcentagem(id, listaPrevisoes[2]['volumes'][i])} for i in range(len(listaPrevisoes[2]['volumes']))]

    response = jsonify({'previsao' : listaPrevisoes[0], 'outorga' : listaPrevisoes[1], 'math' : listaPrevisoes[2], 'volume_morto' : listaPrevisoes[3]})
    response = make_response(response)
    return response

@app.route('/api/reservatorios/<id>/<date>/precisao')
def ma_error(id=None, date=None):
    if id != None and date != None:
        print precisao.mae(id, date)
