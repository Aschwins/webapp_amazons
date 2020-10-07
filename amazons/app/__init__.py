from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

# Configure Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

socketio = SocketIO(app, async_mode='threading')
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models
