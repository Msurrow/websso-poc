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


def decode_and_decrypt_response(SAML_response):
	"""
	We can get a dump of the unencrypted SAML Assertion from the test IDP log.
	No need to waste time on decrypting for this PoC, do discard the input
	SAML_response and return a static non-encrypted (old) saml assertion
	"""
	return """<?xml version="1.0" encoding="UTF-8"?><saml2:Assertion xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion" ID="_e74544f52a7720a2e96460740b31a74e" IssueInstant="2017-07-13T16:12:45.489Z" Version="2.0" xmlns:xs="http://www.w3.org/2001/XMLSchema">
   <saml2:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">https://idp.testshib.org/idp/shibboleth</saml2:Issuer>
   <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:SignedInfo>
         <ds:CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
         <ds:SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
         <ds:Reference URI="#_e74544f52a7720a2e96460740b31a74e">
            <ds:Transforms>
               <ds:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
               <ds:Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#">
                  <ec:InclusiveNamespaces xmlns:ec="http://www.w3.org/2001/10/xml-exc-c14n#" PrefixList="xs"/>
               </ds:Transform>
            </ds:Transforms>
            <ds:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
            <ds:DigestValue>FB+158gKTQf8mH/cAyj79cMM+SZK5KHCGG3FE12MDps=</ds:DigestValue>
         </ds:Reference>
      </ds:SignedInfo>
      <ds:SignatureValue>YCrY0JdyPh6NtaLtlhDm2961KMq6nnA4xgwzktDey1lkcipcaER+OFZKXU54NWFRwifqg8NdhtF7TwwybuMXW66grcn+/Zpm02MpiNK5ZVC3+zY9BqikOXgceYRFROJ3an9zk1gPBkp83qJ8y3XItWB39xWRObn+4Y9F/u4CROQZnRhfb99ZuMyCx3XYPnPqJWWRH0yMGnjCgtGFTraI/kemuxPKJ1ndGSBkyNNWiFbQjWmYWOFfjIBiFGM17ylUhuBjtymAGEk4RReA8vB0duABS1cCuAw+wSOO8W6munnn18da0IFMs1w3cFjFzdSrU+ND9SbAgd8IYgdqomu5uQ==</ds:SignatureValue>
      <ds:KeyInfo>
         <ds:X509Data>
            <ds:X509Certificate>MIIDAzCCAeugAwIBAgIVAPX0G6LuoXnKS0Muei006mVSBXbvMA0GCSqGSIb3DQEBCwUAMBsxGTAX
BgNVBAMMEGlkcC50ZXN0c2hpYi5vcmcwHhcNMTYwODIzMjEyMDU0WhcNMzYwODIzMjEyMDU0WjAb
MRkwFwYDVQQDDBBpZHAudGVzdHNoaWIub3JnMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC
AQEAg9C4J2DiRTEhJAWzPt1S3ryhm3M2P3hPpwJwvt2q948vdTUxhhvNMuc3M3S4WNh6JYBs53R+
YmjqJAII4ShMGNEmlGnSVfHorex7IxikpuDPKV3SNf28mCAZbQrX+hWA+ann/uifVzqXktOjs6Dd
zdBnxoVhniXgC8WCJwKcx6JO/hHsH1rG/0DSDeZFpTTcZHj4S9MlLNUtt5JxRzV/MmmB3ObaX0CM
qsSWUOQeE4nylSlp5RWHCnx70cs9kwz5WrflnbnzCeHU2sdbNotBEeTHot6a2cj/pXlRJIgPsrL/
4VSicPZcGYMJMPoLTJ8mdy6mpR6nbCmP7dVbCIm/DQIDAQABoz4wPDAdBgNVHQ4EFgQUUfaDa2mP
i24x09yWp1OFXmZ2GPswGwYDVR0RBBQwEoIQaWRwLnRlc3RzaGliLm9yZzANBgkqhkiG9w0BAQsF
AAOCAQEASKKgqTxhqBzROZ1eVy++si+eTTUQZU4+8UywSKLia2RattaAPMAcXUjO+3cYOQXLVASd
lJtt+8QPdRkfp8SiJemHPXC8BES83pogJPYEGJsKo19l4XFJHPnPy+Dsn3mlJyOfAa8RyWBS80u5
lrvAcr2TJXt9fXgkYs7BOCigxtZoR8flceGRlAZ4p5FPPxQR6NDYb645jtOTMVr3zgfjP6Wh2dt+
2p04LG7ENJn8/gEwtXVuXCsPoSCDx9Y0QmyXTJNdV1aB0AhORkWPlFYwp+zOyOIR+3m1+pqWFpn0
eT/HrxpdKa74FA3R2kq4R7dXe4G0kUgXTdqXMLRKhDgdmA==</ds:X509Certificate>
         </ds:X509Data>
      </ds:KeyInfo>
   </ds:Signature>
   <saml2:Subject>
      <saml2:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" NameQualifier="https://idp.testshib.org/idp/shibboleth">_564fa532bf9cae9479641237f364c153</saml2:NameID>
      <saml2:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
         <saml2:SubjectConfirmationData Address="128.0.73.57" InResponseTo="a2017-07-13T16:12:35" NotOnOrAfter="2017-07-13T16:17:45.489Z" Recipient="http://websso-poc.herokuapp.com/kai-themes"/>
      </saml2:SubjectConfirmation>
   </saml2:Subject>
   <saml2:Conditions NotBefore="2017-07-13T16:12:45.489Z" NotOnOrAfter="2017-07-13T16:17:45.489Z">
      <saml2:AudienceRestriction>
         <saml2:Audience>websso-poc.herokuapp.com</saml2:Audience>
      </saml2:AudienceRestriction>
   </saml2:Conditions>
   <saml2:AuthnStatement AuthnInstant="2017-07-13T16:12:44.903Z" SessionIndex="_b3a0ebf278d9bb8dae203cf3a60001ef">
      <saml2:SubjectLocality Address="128.0.73.57"/>
      <saml2:AuthnContext>
         <saml2:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml2:AuthnContextClassRef>
      </saml2:AuthnContext>
   </saml2:AuthnStatement>
   <saml2:AttributeStatement>
      <saml2:Attribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">myself</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="eduPersonAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Member</saml2:AttributeValue>
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Staff</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="eduPersonPrincipalName" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">myself@testshib.org</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="sn" Name="urn:oid:2.5.4.4" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">And I</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="eduPersonScopedAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Member@testshib.org</saml2:AttributeValue>
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Staff@testshib.org</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="givenName" Name="urn:oid:2.5.4.42" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Me Myself</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="eduPersonEntitlement" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.7" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">urn:mace:dir:entitlement:common-lib-terms</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="cn" Name="urn:oid:2.5.4.3" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">Me Myself And I</saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="eduPersonTargetedID" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.10" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue>
            <saml2:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" NameQualifier="https://idp.testshib.org/idp/shibboleth" SPNameQualifier="websso-poc.herokuapp.com">l/Bee7BQkVcNH27xh9Wtdn+xKAA=</saml2:NameID>
         </saml2:AttributeValue>
      </saml2:Attribute>
      <saml2:Attribute FriendlyName="telephoneNumber" Name="urn:oid:2.5.4.20" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">
         <saml2:AttributeValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="xs:string">555-5555</saml2:AttributeValue>
      </saml2:Attribute>
   </saml2:AttributeStatement>
</saml2:Assertion>"""