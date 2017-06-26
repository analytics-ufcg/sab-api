from flask import Flask, render_template, redirect, request, session, Response, json, make_response
import sys
sys.path.append('../sab-api/script')
sys.path.append('../sab-api/authentication')
import aux_collection_insert
from hasher import digest, hash_all
from authorize import Authorize
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12)

auth = Authorize("INSA")
completion = False

def get_response(status):
	data = {'Authorized' : status}
	response = json.dumps(data)
	response = make_response(response)
	response.headers['Access-Control-Allow-Origin'] = "*"
	return response
	
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in') == auth.check_session() and session['logged_in'] != False:
		resp = get_response(completion)
		return resp
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        global completion
        completion = auth.authenticate(username, password)
        
        if completion == False:
			resp = get_response(completion)
			return resp
        else:
			session['logged_in'] = auth.gen_session(username)
			resp = get_response(completion)
			return resp
    
@app.route('/logout')
def logout():
	session['logged_in'] = False
	
	global completion
	completion = session['logged_in']
	
	resp = get_response(completion)
	return resp

@app.route('/restrict')
def restrict():
	if not session.get('logged_in'):
		resp = get_response(completion)
		return resp
	else:
		resp = get_response(completion)
		return resp

