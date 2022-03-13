from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from config import Configuration

app = Flask(__name__, static_folder='static')

app.config.from_object(Configuration)

socketio = SocketIO(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)


from blueprints.chat import chat

app.register_blueprint(chat)

import view
