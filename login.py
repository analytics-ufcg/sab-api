from flask import Flask, render_template, redirect, url_for, request, session
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in') == auth.check_session() and session['logged_in'] != False:
		return redirect('../restrict')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = auth.authenticate(username, password)
        if completion == False:
			error = 'Invalid Credentials. Please try again.'
        else:
			session['logged_in'] = auth.gen_session(username)
			return redirect('../restrict')

    return render_template('login.html', error=error)
    
@app.route('/logout')
def logout():
	session['logged_in'] = False
	return redirect('../login')

@app.route('/restrict')
def restrict():
	if not session.get('logged_in'):
		return redirect('../login')
	else:
		return "<a href='/logout'>Logout</a>"

#if __name__ == '__main__':
#    app.run(debug=True)
