from flask import Flask, send_file, request, render_template
import sys

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html", token='')

@app.route('/login_complete')
def login_complete():
	
	# Get the users token
	token = request.args['token']

	# Redirect to index with token
	return render_template("index.html", token=token)

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))


"""

browser --> frontendserver --> webklient --> websso-poc --> webklient --> 
Idp --> redirect til websso-poc. dvs browser indhold er nu websso-poc og ikke frontendserver
direct giver "kontrol" til websso-poc http-server. 

Vi kan putte noget i relay state: det skal være noget der redirecter tilbage til frontendserver
Det kunne være frontendserver.dk/index.html

Løsningsmodel 1: Modificer RelayState
Giver ikke problemer med SOP/CORS
Kan ikke lade sig gøre, hvis IdP kræver signeret requests. 
Konsekvens: Brugerens skal logge ind igen når SAML Token udløbet, og UI bliver nulstillet hvis brugeren 
er igang med at bruge løsningen, når SAML Token udløber.

"""