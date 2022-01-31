from flask import Flask
import os

flag=os.getenv("FLAG")
app = Flask(__name__, static_url_path='/static/')
@app.route("/v1/status")
def index():
	return "Everything is good afaik"

@app.route("/flag")
def flag():
	return flag

if __name__ == '__main__':
	app.run()
