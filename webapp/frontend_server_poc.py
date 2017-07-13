from flask import Flask, send_file
import sys
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
	return send_file("templates/index.html")

if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0",port=int(sys.argv[1]))