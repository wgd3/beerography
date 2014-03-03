from app import app
import json
from flask import render_template,redirect,url_for,flash,request,session
import urllib2,urllib

MY_CLIENT_ID = "C361DB96FBB835383819048F80A189EC40DE1FB2"
MY_CLIENT_SECRET = "9A3A9169B14B23A48C7EECEF2E29692986671872"
ACC_TOKEN = ''

app.secret_key = 'wallace'

@app.route('/', methods=['GET','POST'])
@app.route('/index')
def index():

	# check to see if the session with valid key has been set
	if token in session:
		user = []
		# create query for bais cuser info 
		args = {'access_token':session['token'],'compact':'true'}
		data = urllib.urlencode(args)
		url = 'http://api.untappd.com/v4/user/info?'+data
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		user_json = json.loads(response.read())

		# I think we can just send the json data to the jinja2 template for parsing
		print "Token found in session, sending user json data to page"
		return render_template('index.html',user=user_json)
	
	# session must not be set
	print "No token found in session, return vanilla template"
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
			token_req = urllib2.Request("https://untappd.com/oauth/authorize/?client_id="+MY_CLIENT_ID+"&client_secret="+MY_CLIENT_SECRET+"&response_type=code&redirect_url=http://192.168.2.8:5000/redirect&code="+tempCode)
			
			# open the custom URL and store the result
			token_resp = urllib2.urlopen(token_req)
			
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

	return render_template(url_for('index'))

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

