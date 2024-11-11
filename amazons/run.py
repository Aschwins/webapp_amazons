# from flask import Flask
from flask_bootstrap import Bootstrap
# from flask import make_response
from flask import render_template

# from amazons.util import configure_loggers

# logger = configure_loggers()

# app = Flask(__name__)
# # Bootstrap(app)

# # Bootstrap(app)




# @app.route("/", methods=["GET", "POST"])
# @app.route("/index", methods=["GET", "POST"])
# def index():
#     clients_in_waiting = []
#     logger.debug(f"Clients in waiting: {clients_in_waiting}")
#     resp = make_response(render_template('index.html', waiting=clients_in_waiting))
#     return resp

# @app.route("/onscreen")
# def onscreen():
#     return render_template('onscreen.html')

from flask import Flask

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/index")
def index():
    return "<p>Hello, World!</p>"

@app.route("/onscreen")
def onscreen():
    return render_template('onscreen.html')