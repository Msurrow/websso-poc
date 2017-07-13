from flask import Flask, request, redirect
import base64
import sys
app = Flask(__name__)

"""
Config vars for PoC
"""
idp_url = "https://idp.ssocircle.com:443/sso/SSORedirect/metaAlias/publicidp"
saml_authnrequest = """
<sp:AuthnRequest xmlns:sp="urn:oasis:names:tc:SAML:2.0:protocol" AssertionConsumerServiceIndex="1" ID="really_unique_id_42" ProviderName="SP SSOPoC" Version="2.0">
	<sa:Issuer xmlns:sa="urn:oasis:names:tc:SAML:2.0:assertion">
		http://websso-poc.herokuapp.com/
	</sa:Issuer>
	<sp:NameIDPolicy AllowCreate="true" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">
	</sp:NameIDPolicy>
</sp:AuthnRequest>
"""
saml_authnrequest_b64 = "fZHLasMwEEXXKfQfhPax29CViAPGoWDow9TQbVDtKRaVNeqMlMffV3ZIKV1ke5mZcy6zZq%2FKGAb3Bt8ROIjjaB0r9oWM5BRqNqycHoFV6FRbPj%2BpVXanPGHADq0UJTNQMOgqdBxHoBZobzqoXQ%2FHQt5LUW8LSaCtPe2iM4myM%2F3uYSVFQ7g3PdBLOl%2FIthFt%2B9pgJcU7EKeLhUwoubm9WaxZq5o5Al389HU%2FfbGa1xdDCF7l%2BQE%2BmHHpscsGIPyK2vuswzGfEPkv40z0avKqtw1a051EaS0eqtQjJNdAEaR4RBp1uC4yJaZffs6jyk%2FFOIAL51r5P0oK5%2BzvRzY%2F"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
    	return 'Simple WebSSO PoC. Do a GET to /kai-themes'
    if request.method == 'POST':
    	return "POST request headers: {}<br/><br/>POST request data:{}".format(request.headers, request.data)

@app.route('/kai-themes')
def kai_themes():
	# Check if get request has SAML Token
	saml_token = request.args.get('SAMLResponse')
	if saml_token:
		return '{The list of KAI-themes as JSON}'
	else:
		#saml_authnrequest_b64 = base64.b64encode(bytes(saml_authnrequest, 'utf-8'))
		return redirect("{}?SAMLRequest?={}".format(idp_url,saml_authnrequest_b64))


if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
