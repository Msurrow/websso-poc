from flask import Flask, send_file, request, render_template
import sys

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html", token='')

@app.route('/login_complete')
def login_complete(): # TODO: relay-state kunne være JSON {login_complete_url, originalt requested url (eller noget der fortælle webklienten hvor den skal genoptage sit flow)}
	
	# Get the users token
	token = request.args['token']
	relayState = request.args['relayState']
	
	# Redirect to index with token
	return render_template("index.html", token=token, relayState=relayState)

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))
