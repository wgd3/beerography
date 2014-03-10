import urllib,urllib2,httplib

class urlbuilder:

	def __init__(self):
		self.name = "testing"

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
			response = urllib2.urlopen(data_request)
		
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
