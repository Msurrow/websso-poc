def generate_SAML_AuthnRequest():
	saml_authnrequest_template = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><samlp:AuthnRequest xmlns:samlp=\"urn:oasis:names:tc:SAML:2.0:protocol\" xmlns:saml=\"urn:oasis:names:tc:SAML:2.0:assertion\" AssertionConsumerServiceURL=\"http://websso-poc.herokuapp.com/kai-themes\" IssueInstant=\"{}\" ID=\"a{}\" > <saml:Issuer >websso-poc.herokuapp.com</saml:Issuer> </samlp:AuthnRequest >"
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
