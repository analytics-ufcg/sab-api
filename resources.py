#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, make_response, request, Response, json, redirect, url_for
from werkzeug.utils import secure_filename
import api_mandacaru
import StringIO
import csv
import re
import os

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['csv'])
UPLOAD_FOLDER = '/home/diegoc/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            monitoramento = file.read()
            isValido = True
            regex = re.compile(r"^\d+(.\d+)?,\d+(.\d+)?,[A-Z ]*,\d\d\/\d\d\/\d\d\d\d")
            monitoramentoList = monitoramento.split('\n')
            for i in range(1,len(monitoramentoList) -1):
                if regex.search(monitoramentoList[i]) == None:
                    isValido = False
            saida = {"valido": isValido, "arquivo": file.filename, "linhas":len(monitoramentoList)}
            response = json.dumps(saida)
            response = make_response(response)
            response.headers['Access-Control-Allow-Origin'] = "*"
	return response
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

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
