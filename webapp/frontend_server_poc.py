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
