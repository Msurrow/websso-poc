from flask import Flask, request, redirect, jsonify
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import sys
import helpers

app = Flask(__name__)
CORS(app)

very_important_kai_data = ['KAI-Tema 01', 'KAI-Tema 02', 'KAI-Tema 03']

"""
index -function handles the root endpoint ('/'). It is only set-up to 
handle GET and display a very basic landing page. 
"""
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
    	return '<h1>Simple WebSSO PoC</h1><br/><br/>Do a GET to /kai-themes'

"""
kai_themes -funtion handles the '/kai-themes' endpoint. It simulates an endpoint
on the KAI service. It will authenticate the user request, and if successful 
return a JSON response.
"""
@app.route('/kai-themes', methods=['GET','POST'])
def kai_themes():
	# Client attempts to get data from endpoint.
	# Check if client is logged in and if so return the requested data
	if helpers.do_authentication(request):
		return jsonify(very_important_kai_data)
	else:
		# Return SAML response to start login process
		return helpers.get_SAML_AuthnRequest()
"""
handle_saml_response -function handles SAML Responses POST'ed to the Service Provider
from the IdP.
"""
@app.route('/saml_login_success', methods=['POST'])
def handle_saml_response():
	print("POST request headers:\n{}\nPOST request form:\n{}\nPOST request args:\n{}\n".format(request.headers, list(request.form.items()), list(request.args.items())))
	
	saml_response = request.form.get('SAMLResponse')
	relay_state = request.form.get('RelayState')

	# Check if there is a SAML token in the request
	if saml_response:
		# Validate SAML Assertion
		saml_response_decrypted = helpers.decode_and_decrypt_response(saml_response)
		
		# Extract information from SAML Assertion.
		# This is where you'd normally parse the SAML Assertion for all the information
		# you need and use that properly. 
		soup = BeautifulSoup(saml_response_decrypted, 'xml')
		saml_subject_name = soup.findAll("Attribute", {"FriendlyName":"uid"})[0].text.lstrip().rstrip()

		# Generate a token to return to the user, for use with further API requests
		# 	Token should have a Time-To-Live that is at most the TTL of the SAML Token
		#	This is NOT an example of how to generate a token
		token = "super_secret_token_beloging_to_{}".format(saml_subject_name)
		
		# Redirect to the server in RelayState with token (assumes frontendserver set the RelayState correct)
		return redirect(relay_state+"?token="+token)
	else:
		# Expected SAML Response but found none.
		return abort(400)

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
