from app import app
import json
from flask import render_template,redirect,url_for,flash,request
from brewerydb import *

# Set up brewerydb connection
BreweryDb.configure("83d7702a58244b96d38c625c9a474355")

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
	if request.method == 'POST':
		beerQuery = request.form['beer-search']
		if (beerQuery != ''):
			beerResults = BreweryDb.search({'type':'beer','q':beerQuery})
			#flash('Query on successful')
			return render_template('index.html', results=beerResults, query=beerQuery)
		else:
			flash('There was a problem with your search')
	
	return render_template('index.html')

@app.route('/testing')
def testing():

	# Raleigh coords
	testLat = 35.855257099999996
	testLong = -78.7189141
	range = 30
	units = 'mi'
	geo = 1

	# get sample results
	localBrews = BreweryDb.search({'type':'beer','q':'hoppyum'})
	print "Found this many breweries:"+str(localBrews)

	# beer search testing
	#foundBeers = BreweryDb.search({'type': 'beer','q':'Lonerider'})
	#print "Found some beer: "+str(foundBeers)

	return render_template('testing.html',results=localBrews)
