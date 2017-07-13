from flask import Flask, request, redirect
import base64
import sys
app = Flask(__name__)

"""
Config vars for PoC
"""
idp_url = "https://idp.ssocircle.com:443/sso/SSORedirect/metaAlias/publicidp"
saml_authnrequest = """
<samlp:AuthnRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" 
					xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" 
					ID="aaf23196-1773-2113-474a-fe114412ab72" 
					Version="2.0"
					ProviderName="SP_SSO_PoC"
					IssueInstant="2004-12-05T09:21:59" 
					AssertionConsumerServiceIndex="1">
	<saml:Issuer>
		https://idp.ssocircle.com
	</saml:Issuer>
	<samlp:NameIDPolicy AllowCreate="true" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"/>
</samlp:AuthnRequest>
"""
saml_authnrequest_b64 = "fZHNasMwEITPKfQdjO6KLcWpiYgDJqFg6I%2BpS69BtTdEYEuuVk7Tt6%2BcNC7tIbppd76Z1WqJsm06kfVur1%2Fgowd0wbFtNIpTIyW91cJIVCi0bAGFq0SZPT4IPo1EZ40zlWlIcHszGc4veR2UiGCdMnok801KpNzxGVvcUZYkM8oZm9E4iSXdAWNxzLh8T%2FgIvIFFb5AS70d%2BaoU1B1WDffKBKSmLbVk%2BbwuzvvRzxB5yjU5q58EoiinjNJq%2FRgvBmZgvRvfsMuDaaOxbsCXYg6o8XMMxJYysvHA5PFScTO1wn%2Byd61CEoaq7KaKplK0amFamHcThP%2FXyvPlh1nxTmEZVX0HWNOZzbUE6P7%2BzPZDg3thWuuvrHCqqpruTVDgrNSrQjoQ%2B55z794dX3w%3D%3D"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
    	return 'Simple WebSSO PoC. Do a GET to /kai-themes'
    if request.method == 'POST':
    	return "POST request headers: {}\n\n\nPOST request data:{}".format(request.headers, request.data)

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
