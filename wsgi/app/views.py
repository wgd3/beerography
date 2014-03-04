from app import app
import json
from flask import render_template,redirect,url_for,flash,request
import urllib2

MY_CLIENT_ID = "C361DB96FBB835383819048F80A189EC40DE1FB2"
MY_CLIENT_SECRET = "9A3A9169B14B23A48C7EECEF2E29692986671872"
ACC_TOKEN = ''

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


	return render_template('testing.html',client_id=MY_CLIENT_ID)

@app.route('/redirect', methods=['GET'])
def redirect():
	if request.method == 'GET':
		print "Detected GET request on /redirect"
		tempCode = request.args.get("code")
		if tempCode != '':
			
			print "Found tempCode in request: " + tempCode
			print "Getting token code..."
			# create Request object with custom URL
			token_req = urllib2.Request("https://untappd.com/oauth/authorize/?client_id="+MY_CLIENT_ID+"&client_secret="+MY_CLIENT_SECRET+"&response_type=code&redirect_url=http://localhost:5000/redirect&code="+tempCode)
			
			# open the custom URL and store the result
			token_resp = urllib2.urlopen(token_req)
			
			# grab the data from the response and parse it in JSON format
			data = json.loads(token_resp.read())
			
			# update the ACC_TOKEN variable
			print data['response']
			ACC_TOKEN = data['response']['access_token']
			print "Token code found: " + ACC_TOKEN	
		
		else:
			flash("Error getting tempCode for access token")
			print "Error while obtaining tempCode"
	else:
		print "Non-GET method for /redirect"
		flash("Error with redirect")

	return render_template('testing.html')



