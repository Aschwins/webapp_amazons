from flask_bootstrap import Bootstrap
from flask import render_template, Flask


app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/onscreen")
def onscreen():
    return render_template('onscreen.html')