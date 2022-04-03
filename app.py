from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from config import Configuration

# App & Socketio initialisation
app = Flask(__name__, static_folder='static')
app.config.from_object(Configuration)
socketio = SocketIO(app)

# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Current_user authenticating
login_manager = LoginManager(app)

# Flask-admin
import admin

# Blueprints initialisation
from blueprints.api import api
from blueprints.chat import chat

app.register_blueprint(chat)
app.register_blueprint(api)

# Routing
import view