from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

# Configure Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

socketio = SocketIO(app, async_mode='threading')

from amazons import routes
