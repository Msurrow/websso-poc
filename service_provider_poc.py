from flask import Flask, request, redirect, jsonify
from flask_cors import CORS, cross_origin
import base64,uuid
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup
import helpers

app = Flask(__name__)
CORS(app)

idp_url = "https://idp.testshib.org/idp/profile/SAML2/POST/SSO"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
    	return 'Simple WebSSO PoC. Do a GET to /kai-themes'
    if request.method == 'POST':
    	return "POST request headers:\n{}\n\n<br/><br/>POST request data:\n{}\n\n<br/><br/>POST request args:\n{}\n\n<br/><br/>".format(request.headers, list(request.form.items()), list(request.args.items()))

def decode_and_decrypt_response(SAML_response):
	"""
	We can get a dump of the unencrypted SAML Assertion from the test IDP log.
	No need to waste time on decrypting for this PoC, do discard the input
	SAML_response and return a static non-encrypted (old) saml assertion
	"""
	return open('saml_response_example.xml', 'r').read()

@app.route('/kai-themes', methods=['GET','POST'])
def kai_themes():
	print("POST request headers:\n{}\nPOST request form:\n{}\nPOST request args:\n{}\n".format(request.headers, list(request.form.items()), list(request.args.items())))
	
	saml_response = request.form.get('SAMLResponse')
	relay_state = request.form.get('RelayState')

	# Check if there is a SAML token in the request
	if saml_response:
		# Validate SAML Assertion
		saml_response_decrypted = decode_and_decrypt_response(saml_response)
		
		# Extract information from SAML Assertion
		soup = BeautifulSoup(saml_response_decrypted, 'xml')
		saml_subject_name = soup.findAll("Attribute", {"FriendlyName":"uid"})[0].text.lstrip().rstrip()

		# Generate a token to return to the user, for use with further API requests
		# 	Token should have a Time-To-Live that is at most the TTL of the SAML Token
		#	This is NOT an example of how to generate a token
		token = "super_secret_token_beloging_to_{}".format(saml_subject_name)
		
		# Redirect to the server in RelayState with token (assumes frontendserver set the RelayState correct)
		return redirect(relay_state+"?token="+token)
	else:
		# Client attempts to get data from endpoint.
		# Check if client is logged in
		if (request.args['token']):
			# Client has a valid token and is logged in
			kai_data = ['KAI-Tema 01', 'KAI-Tema 02', 'KAI-Tema 03']
			return jsonify(kai_data)
		else:
			# Client do not have valid token. Start SAML login procedure
			# Respond with SAML AuthnRequest through SAML POST binding.

			issueInstant = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
			#msg_id = str(uuid.uuid1())
			saml_authnrequest_template = helpers.generate_SAML_AuthnRequest()
			saml_authnrequest = saml_authnrequest_template.format(issueInstant,issueInstant) #UUID as ID gave problems. timestamp is unique enough for this PoC (one message per second)
			saml_authnrequest_encoded = base64.b64encode(bytes(saml_authnrequest, 'utf-8')).decode('utf-8')

			return '''
				<form method="post" action="{}">
					<input type="hidden" name="SAMLRequest" value="{}" />
					<input type="hidden" name="RelayState" value="" />
					<input type="submit" value="Submit" />
				</form>
			'''.format(idp_url,saml_authnrequest_encoded)

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
