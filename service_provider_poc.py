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
    	return "POST request headers:\n{}<br/><br/>POST request data:\n{}<br/><br/>REQUEST ARGS:{}".format(request.headers, request.data, list(request.args.items()))

@app.route('/kai-themes', methods=['GET','POST'])
def kai_themes():
	# Check if get request has SAML Token
	print("REQUEST HEADERS: {}\n\nPOST request data:\n{}\n\nREQUEST ARGS:{}".format(request.headers, request.data, list(request.args.items())))
	
	saml_token = request.args.get('SAMLResponse')
	if saml_token:
		return '{The list of KAI-themes as JSON}'
	else:
		issueInstant = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
		msg_id = str(uuid.uuid1())
		saml_authnrequest = saml_authnrequest_template.format(issueInstant,issueInstant)
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
