from flask import Flask, request, redirect
from flask_cors import CORS, cross_origin
import base64,uuid
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

idp_url = "https://idp.testshib.org/idp/profile/SAML2/POST/SSO"

saml_authnrequest_template = "<samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" AssertionConsumerServiceURL=\"http://websso-poc.herokuapp.com/kai-themes\" IssueInstant=\"{}\" ID=\"a{}\" > <saml:Issuer > websso-poc.herokuapp.com </saml:Issuer> </samlp:AuthnRequest >"

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
		


		return '<h3>Logged in as {}</h3><h4>The list of KAI-themes as JSON</h4><div><ul><li>KAI-tema01</li><li>KAI-tema02</li></ul></div>'.format(saml_subject_name)
	else:
		issueInstant = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
		#msg_id = str(uuid.uuid1())
		saml_authnrequest = saml_authnrequest_template.format(issueInstant,issueInstant) #UUID as ID gave problems. timestamp is unique enough for this PoC (one message per second)
		saml_authnrequest_encoded = base64.b64encode(bytes(saml_authnrequest, 'utf-8')).decode('utf-8')

		return '''
			<form method="post" action="{}">
				<input type="hidden" name="SAMLRequest" value="{}" />
				<input type="hidden" name="RelayState" value="token007" />
				<input type="submit" value="Submit" />
			</form>
		'''.format(idp_url,saml_authnrequest_encoded)

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
