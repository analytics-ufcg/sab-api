from flask import Flask, redirect, session
from flask_digest import Stomach
import requests

app = Flask(__name__)
stomach = Stomach('INSA')

db = dict()
query_name = "SELECT username FROM tab_user;"
query_pass = "SELECT password FROM tab_user;"

@stomach.register
def add_user(username, password):
    db[username] = password

@stomach.access
def get_user(username):
    return db.get(username, None)
    
@app.route('/auth')
@stomach.protect
def authenticate(username, password):
	return redirect('http://google.com')
    
@app.route('/login', methods=['GET', 'POST'])
def main():
	if request.method == 'POST':
		username = request.form['username']
        password = request.form['password']
        authenticate(username, password)
	return render_template('login.html')


add_user('admin', '12345')
#add_user('admin', '12345')
#app.run()
