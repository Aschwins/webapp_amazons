## Run command
## FLASK_APP=src/amazons/app.py FLASK_ENV=development flask run
import os

from flask import Flask, jsonify, request
from flask import render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/hello/<name>", methods=["GET"])
def get_hello(name):
    return f"Hello {name}"


@app.route("/game")
def helloworld():
    return render_template('game.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
