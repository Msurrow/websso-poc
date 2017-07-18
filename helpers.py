import base64,uuid
import sys
from time import gmtime, strftime

def generate_SAML_AuthnRequest():
	saml_authnrequest_template = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" AssertionConsumerServiceURL=\"http://websso-poc.herokuapp.com/saml_login_success\" IssueInstant=\"{}\" ID=\"a{}\" > <saml:Issuer >websso-poc.herokuapp.com</saml:Issuer> </samlp:AuthnRequest >"
	return saml_authnrequest_template

	""" 
	The test IdP XML validator is throwing some unexplained errors
	if the above XML is not exactly as above (e.g. a different 
	whitespace may result in an error). Below is a pretty print of 
	the XML.

	<samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" 
						xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" 
						AssertionConsumerServiceURL=\"http://websso-poc.herokuapp.com/kai-themes\" 
						IssueInstant=\"{}\" 
						ID=\"a{}\" > 
		<saml:Issuer > websso-poc.herokuapp.com </saml:Issuer> 
	</samlp:AuthnRequest >

	NB: This is a bare minimum that needs to be in the SAML AuthnRequest 
	for the example to work. A proper SAML AuthnRequest have more elements
	and attrbutes. See SAML 2.0 Core for specificaion of SAML AuthnRequest.
	Here: http://www.oasis-open.org/committees/download.php/56776/sstc-saml-core-errata-2.0-wd-07.pdf

	"""
"""
Function for validating tokens. Faked in this PoC.
"""
def validate_token(token):
	# We fake it here. See readme for details on what _can_ be done with
	# tokens.
	print("Endpoint called with token {}, which upon critical inspection seems valid.".format(token))
	return true

"""
Function do base64-decode and decrypt the SAML Response from the (test) IdP.
Faked in this Poc.
"""
def decode_and_decrypt_response(SAML_response):
	"""
	We get an encrypted SAML Assertion from the test IdP, but 
	we can get a dump of the unencrypted SAML Assertion from the test IDP log.
	No need to waste time on decrypting for this PoC, so fake it and ignore 
	the input SAML_response and return a static non-encrypted (old) saml assertion.
	"""
	return open('saml_response_example.xml', 'r').read()

"""
Does authentication of a request ("check for existing security context" in SAML terms).
- If the request contains a Token, the token is validated.
- If the request does not contain a Token, the SAML WebSSO profile process is started, that is, the 
	client is redirected to the IdP.
"""
def do_authentication(request):
	token = request.args['token']
	if token:
		validate_token(token)
		# Client has a valid token and is logged in
		return true
	else:
		# Client do not have a token. Start SAML login procedure
		# Respond with SAML AuthnRequest through SAML POST binding.

		issueInstant = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
		#msg_id = str(uuid.uuid1())
		saml_authnrequest_template = helpers.generate_SAML_AuthnRequest()
		saml_authnrequest = saml_authnrequest_template.format(issueInstant,issueInstant) #UUID as ID gave problems. timestamp is unique enough for this PoC (one message per second)
		saml_authnrequest_encoded = base64.b64encode(bytes(saml_authnrequest, 'utf-8')).decode('utf-8')

		return '''
			<b>Du er ikke logget ind! Tryk på login-knappen nedenfor for at blive viderestillet til login-siden</b>
			<form method="post" action="{}">
				<input type="hidden" name="SAMLRequest" value="{}" />
				<input type="hidden" name="RelayState" value="" />
				<input type="submit" value="Login" />
			</form>
		'''.format(idp_url,saml_authnrequest_encoded)

