from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from chat.blueprint import chat

from config import Configuration

app = Flask(__name__)

app.config.from_object(Configuration)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)

app.register_blueprint(chat, url_prefix='/chat')
