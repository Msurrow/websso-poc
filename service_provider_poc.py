from flask import Flask, request, redirect
import base64,uuid
import sys
from time import gmtime, strftime
app = Flask(__name__)

"""
Config vars for PoC
"""
idp_url = "https://idp.testshib.org/idp/profile/SAML2/POST/SSO"
# authnrequest_ID = ""
# authnrequest_issueInstant = "" #Format from SSOCircle example: 2017-07-13T18:35:07Z
# authnrequest_binding = "" #From SSOCircle example: SAML2_BINDINGS_POST
# authnrequest_assertionConsumerServiceURL = ""
# authnrequest_issuer = ""
# authnrequest_spNameQualifier = ""

saml_authnrequest_template = "<samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" AssertionConsumerServiceURL=\"http://websso-poc.herokuapp.com/kai-themes\" IssueInstant=\"{}\" ID=\"a{}\" > <saml:Issuer > websso-poc.herokuapp.com </saml:Issuer> </samlp:AuthnRequest >"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
    	return 'Simple WebSSO PoC. Do a GET to /kai-themes'
    if request.method == 'POST':
    	return "POST request headers:\n{}\n\n<br/><br/>POST request data:\n{}\n\n<br/><br/>POST request args:\n{}\n\n<br/><br/>".format(request.headers, list(request.form.items()), list(request.args.items()))

@app.route('/kai-themes', methods=['GET','POST'])
def kai_themes():
	# Check if get request has SAML Token
	print("POST request headers:\n{}\nPOST request form:\n{}\nPOST request args:\n{}\n".format(request.headers, list(request.form.items()), list(request.args.items())))
	
	saml_reponse = request.form.get('SAMLResponse')
	replay_state = request.form.get('ReplayState')
	print("SAML_RESPONSE: {}".format(saml_reponse))

	if saml_reponse:
		# Will be base64 encoded.
		saml_reponse_decoded = base64.b64decode(saml_reponse).decode('utf-8')
		print("This is the SAML Response decoded: {}".format(saml_reponse_decoded))
		return '{The list of KAI-themes as JSON}'
	else:
		issueInstant = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
		#msg_id = str(uuid.uuid1())
		saml_authnrequest = saml_authnrequest_template.format(issueInstant,issueInstant) #UUID as ID gave problems. timestamp is unique enough for this PoC (one message per second)
		saml_authnrequest_encoded = base64.b64encode(bytes(saml_authnrequest, 'utf-8')).decode('utf-8')
		#return redirect("{}?SAMLRequest={}".format(idp_url,saml_authnrequest_encoded))
		#return "{}?SAMLRequest={}".format(idp_url,saml_authnrequest_encoded)
		return '''
			<form method="post" action="{}">
				<input type="hidden" name="SAMLRequest" value="{}" />
				<input type="hidden" name="RelayState" value="token007" />
				<input type="submit" value="Submit" />
			</form>
		'''.format(idp_url,saml_authnrequest_encoded)


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))


"""
XML Response example:
<?xml version="1.0" encoding="UTF-8"?>
	<saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" Destination="http://websso-poc.herokuapp.com/kai-themes" ID="_64ed5bfda15b5325dadc93831869ef56" InResponseTo="a2017-07-13T15:47:30" IssueInstant="2017-07-13T15:47:34.156Z" Version="2.0">
	<saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">
		https://idp.testshib.org/idp/shibboleth
	</saml2:Issuer>
	<saml2p:Status>
		<saml2p:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Responder"/>
		<saml2p:StatusMessage>Unable to encrypt assertion</saml2p:StatusMessage>
	</saml2p:Status>
</saml2p:Response>
"""