from datetime import datetime

from flask_login import UserMixin, current_user

from app import db


class ChatParticipation(db.Model, UserMixin):
    __tablename__ = 'chat_participation'
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    recipient_id = db.Column(db.Integer)

    user = db.relationship('User', backref='chat_participations')
    chat = db.relationship('Chat', backref='user_participations')


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"id: {self.id} login: {self.login}"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'login': self.login
        }


class Chat(db.Model, UserMixin):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='chats', secondary='chat_participation', viewonly=True)

    def __repr__(self):
        return f"{self.id}"


class Message(db.Model, UserMixin):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship('Chat', backref='messages')
    user = db.relationship('User', backref='messages')

    def __repr__(self):
        return f"id: {self.id}, sender_id: {self.sender_id}, content: {self.content}"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'sender': current_user.serialize,
            'content': self.content,
            'is_read': self.is_read,
            'date': {'year': self.date.year, 'month': self.date.month, 'day': self.date.day, 'hour': self.date.hour,
                     'minute': self.date.minute}
        }
