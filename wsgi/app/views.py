from app import app
from flask import render_template,request,redirect,url_for,flash


@app.route('/')
@app.route('/index')
def index():
	return "Hello, World!"

@app.route('/testing')
def testing():
	return render_template('testing.html')
