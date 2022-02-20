from datetime import datetime

from flask_login import UserMixin

from app import db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.id} {self.login}"

# Chat and Chat_member models yet not ready.
class Chat(db.Model, UserMixin):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)

    member = db.relationship("Chat_member", backref="chat")

    def __repr__(self):
        return f"{self.id}"

class Chat_member(db.Model, UserMixin):
    __tablename__ = 'chat_member'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)

    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))
    def __repr__(self):
        return f"{self.id}"