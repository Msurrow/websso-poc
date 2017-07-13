from flask import Flask, request, redirect
import base64,uuid
import sys
from time import gmtime, strftime
from bs4 import BeautifulSoup

app = Flask(__name__)

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
	replay_state = request.form.get('ReplayState')

	if saml_response:
		saml_response_decrypted = decode_and_decrypt_response(saml_response)
		
		soup = BeautifulSoup(saml_response_decrypted, 'xml')
		saml_subject_name = soup.findAll("Attribute", {"FriendlyName":"uid"})[0].text.lstrip().rstrip()

		return '<h3>Logged in as {}</h3><h4>The list of KAI-themes as JSON</h4><div><ul><li>KAI-tema01</li><li>KAI-tema02</li></ul></div>{}'.format(saml_subject_name)
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
