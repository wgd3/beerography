from app import app
import json
from flask import Flask,request,render_template,redirect,url_for,flash,session
import urllib2
import urllib,httplib

MY_CLIENT_ID = "C361DB96FBB835383819048F80A189EC40DE1FB2"
MY_CLIENT_SECRET = "9A3A9169B14B23A48C7EECEF2E29692986671872"
ACC_TOKEN = ''
GOOGLE_API = 'AIzaSyA8WHx49VXTHoaoIdZfvH56HdTC5IFVz-U'

app.config['SECRET_KEY'] = 'wallace'

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():

	# these are variables that are passed to the page on load. the code below checks to see if we have data for the variables
	user = ''
	beers = ''

	# See if someone is logged in. If so, retreive their info and display it
	if 'json' in session:
		user = session['json']

	# if it's a post method, someone submitted a search query
	if request.method == 'POST':
		log_untappd_debug("Detected POST request on index.html, looking for beer!")

		# user searched for something
		search_query = request.form['beer-search']
		search_result = untappd_url('search/beer',{'p':search_query,'sort':'count'})
		if search_result == False:
			# The above variable is assigned False if something went wrong with the request
			flash('POST request failed - results not returned','error')
		else:	
			log_untappd_debug("Grabbed JSON search results, found "+search_result['response']['beers']['count']+' results')		
			beer_results = search_result['response']['beers']
			
			for x in range(1, search_result['response']['beers']['count']):
				# Create a list of JSON formatted beer objects so it's easier to parse in Jinja2 template
				beers.append(beer_results['items'][x])

	print "Completed index() method, rendering index template"
	return render_template('index.html',
				user=user,
				beers=beers,
				client_id=MY_CLIENT_ID)

@app.route('/logout')
def session_logout():
	if 'token' in session:
		session.pop('token', None)
		flash("Logged out successfully",'success')
	else:
		flash('Logout called when no token was found in user session','error')
		print "/redirect was requested but no token was found in the session"

	return redirect(url_for('index'))

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

			# Populate user session cookie for caching purposes
			session['token'] = ACC_TOKEN
			populate_user_cookie()				

			flash('Logged in successfully','success')
			loginSuccess = True
		else:
			flash("Error getting tempCode for access token",'error')
			print "Error while obtaining tempCode"
			loginSuccess = False
	else:
		print "Non-GET method for /redirect"
		flash("Error with redirect",'error')

	return redirect(url_for('index'))

def untappd_url(method, query_dict):
	'''
	Method for building Untappd query and return JSON formatted results. 
	This method will also check for whether or not a user is authenticated.
	'''
	log_untappd_debug("Building Untappd URL query")
	log_untappd_debug("Method: "+method)
	log_untappd_debug("Arguments: "+str(query_dict))

	base_url = 'http://api.untappd.com/v4/'+method+'?'
	
	# Check to see if user is logged in
	if 'token' in session:
                # create query for logged in user
		log_untappd_debug("Found token in session, creating authenticated request")
                auth_dict = {'access_token':session['token']}
	else: 
		# create query for unauthenticated user
		log_untappd_debug("No token found in session, creating unauthenticated request")
		auth_dict = {'client_id':MY_CLIENT_ID,'client_secret':MY_CLIENT_SECRET}

	# merge dictionaries
	merged_dict = dict(auth_dict,**query_dict)
	log_untappd_debug("Merged dictionary value: "+str(merged_dict))

	# encode URL arguments
	encoded_args = urllib.urlencode(merged_dict)

	# pull entire URL together
	full_url = base_url+encoded_args
	log_untappd_debug("Full URL query: "+full_url)

	# wrap request/response in try loop so the server doesn't crap out
        try:
		request = urllib2.Request(full_url)
        	response = urllib2.urlopen(request)
        
		# JSON-ify the output for easier parsing
		json_reaponse = json.loads(response.read())	

		return json_response
	except urllib2.HTTPError, e:
                log_untappd_error('HTTPError = ' + str(e.code))
        except urllib2.URLError, e:
                log_untappd_error('URLError = ' + str(e.reason))
        except httplib.HTTPException, e:
		log_untappd_error('HTTPException')
        except Exception:
                import traceback
                log_untappd_error("Traceback: "+traceback.format_exc())
        
	return False

def populate_user_cookie():
	'''
	For caching purposes, we'll keep stuff in the authenticated cookie instead of hitting
	untappd every time we need something
	'''
	if 'token' in session:
		log_untappd_debug("Working on populating user cookie, token found")
		
		# Grab JSON user info
		json_user = untappd_url('user/info',{'compact':'true'})
		if json_user == False:
			log_untappd_error("We're trying to set up the user cookie, but there was an issue grabbing the user data.")
			return False
		else:
			log_untappd_debug("Grabbed JSON user info for "+json_user['response']['user']['user_name'])
	
		# Store just the user-specific data to be passed to index.html
		user = json_user['response']['user']
		session['json'] = user
		session['user_name'] = user['user_name']
		session['first_name'] = user['first_name']
		session['last_name'] = user['last_name']
		session['user_avatar'] = user['user_avatar']
		log_untappd_debug("Set cookie for "+session['first_name']+" "+session['last_name'])
		return True

	log_untappd_error("Somehow we tried to populate the user cookie, and there wasn't a token in the session already")
	return False

def log_untappd_debug(message):
	'''
	Simple method for logging Untappd-related debug messages
	'''
	print "[Untappd][DEBUG] "+message
	return True

def log_untappd_error(message):
	'''
	Log Untappd-related errors
	'''
	print "[Untappd][ERROR] "+message
	return True

def log_google_debug(message):
	'''
	Return Google API related debug messages
	'''
	return "[Google][DEBUG] "+message

def log_google_error(message):
	'''
	Return Google API related errors
	'''
	return "[Google][ERROR] "+message
