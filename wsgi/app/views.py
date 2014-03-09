from app import app
import json
from flask import Flask,request,render_template,redirect,url_for,flash,session
import urllib2
import urllib

MY_CLIENT_ID = "C361DB96FBB835383819048F80A189EC40DE1FB2"
MY_CLIENT_SECRET = "9A3A9169B14B23A48C7EECEF2E29692986671872"
ACC_TOKEN = ''

app.config['SECRET_KEY'] = 'wallace'

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():

	# these are variables that are passed to the page on load. the code below checks to see if we have data for the variables
	user = []

	# check to see if the session with valid key has been set
	if 'token' in session:
		# create query for basic user info 
		args = {'access_token':session['token'],'compact':'true'}
		data = urllib.urlencode(args)
		url = 'http://api.untappd.com/v4/user/info?'+data
		data_request = urllib2.Request(url)
		try: 
    			response = urllib2.urlopen(data_request)
			user_json = json.loads(response.read())
			user = user_json['response']['user']

			# I think we can just send the json data to the jinja2 template for parsing
			print "Token found in session, sending user json data to page"
			print "json: "+str(user_json)

			# store basic data
			uName = user_json['response']['user']['user_name']
			print "Found user: "+uName
		except urllib2.HTTPError, e:
    			print 'HTTPError = ' + str(e.code)
		except urllib2.URLError, e:
    			print 'URLError = ' + str(e.reason)
		except httplib.HTTPException, e:
    			print 'HTTPException'
		except Exception:
    			import traceback
    			print 'generic exception: ' + traceback.format_exc()

	else:	
		# session must not be set
		print "No token found in session, return vanilla template"
	

	# if it's a post method, someone submitted a search query
	beers = []
	if request.method == 'POST':
		print "Detected POST request on index, looking for beer!"
		# user searched for something
		query = request.form['beer-search']
		# build args for untappd query
		if 'token' in session:
			print "Building authenticated query"
			args = {'access_token':session['token'],'q':query}
		else:
			print "No token found, creating a non-auth'd request"
			args = {'q':query}

		data = urllib.urlencode(args)
		url = 'http://api.untappd.com/v4/search/beer?'+data
		data_request = urllib2.Request(url)
		response = urllib2.urlopen(data_request)
		json_response = json.loads(response.read())
		query_results = json_response['response']['beers']
#		print "DEBUG: "+str(len(query_results['items']))
		for x in range(1, json_response['response']['beers']['count']):
			print query_results['items'][x]
			beers.append(query_results['items'][x])

	print "Made it through session checking, rendering index template"
	return render_template('index.html',
				user=user,
				beers=beers,
				client_id=MY_CLIENT_ID)

@app.route('/logout')
def session_logout():
	if 'token' in session:
		session.pop('token', None)
		flash("Logged out successfully")
	else:
		flash('Logout called when no token was found in user session','error')
		print "/redirect was requested but no token was found in the session"

	return redirect(url_for('index'))

@app.route('/search',methods=['GET','POST'])
def search():

	print "Loading search page"
	#print request.method
	query = request.form['beer-search']
	# build args for untappd query
	args = {'access_token':session['token'],'q':query}
	data = urllib.urlencode(args)
	url = 'http://api.untappd.com/v4/search/beer?'+data
	data_request = urllib2.Request(url)
	response = urllib2.urlopen(data_request)
	json_response = json.loads(response.read())
	beers = json_response['response']['beers']['items']

	breweries = json_response['response']['breweries']

	return render_template('index.html',beers=beers,breweries=breweries)

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
def login():
	if request.method == 'GET':
		print "Detected GET request on /redirect"
		tempCode = request.args.get("code")
		if tempCode != '':
			
			print "Found tempCode in request: " + tempCode
			# create Request object with custom URL
			token_req = urllib2.Request("https://untappd.com/oauth/authorize/?client_id="+MY_CLIENT_ID+"&client_secret="+MY_CLIENT_SECRET+"&response_type=code&redirect_url=http://beerography-wdaniel.rhcloud.com/redirect&code="+tempCode)
			
			# open the custom URL and store the result
			token_resp = urllib2.urlopen(token_req)
			print str(token_resp)			
	
			# grab the data from the response and parse it in JSON format
			data = json.loads(token_resp.read())
			
			# update the ACC_TOKEN variable
			print data['response']
			ACC_TOKEN = data['response']['access_token']
			print "Token code found: " + ACC_TOKEN	
			session['token'] = ACC_TOKEN	
			flash('Logged in successfully')
			loginSuccess = True
		else:
			flash("Error getting tempCode for access token")
			print "Error while obtaining tempCode"
			loginSuccess = False
	else:
		print "Non-GET method for /redirect"
		flash("Error with redirect")

	return redirect(url_for('index'))

@app.route('/testuser')
def loggedin():

	if 'token' in session:
		# Set obvious logged in variable because a session token was found
		loggedIn = True

		# Create URL args for user info
		user_args = {'access_token':session['token'],'compact':'true'}
		data = urllib.urlencode(user_args)
		print "Encoded: "+str(data)
		url = 'http://api.untappd.com/v4/user/info?'+data
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		user_info = json.loads(response.read())

		# for debugging, print some shit
		print "Found some data: "+str(user_info['response']['user'])
	else:
		loggedIn = False
	return render_template('testuser.html',loggedIn=loggedIn)

