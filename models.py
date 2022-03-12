from datetime import datetime

from flask_login import UserMixin

from app import db


class ChatParticipation(db.Model, UserMixin):
    __tablename__ = 'chat_participation'

    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'), primary_key=True)
    chat = db.relationship('Chat',
                           backref='users_participation')

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    sender = db.relationship('User',
                             backref='chats_participation')

    recipient_id = db.Column(db.Integer)


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


class Notification(db.Model, UserMixin):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('User', backref='notifications')

    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"id: {self.id} title: {self.title}"


class MessageNotification(db.Model, UserMixin):
    __tablename__ = 'message_notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    chat_id = db.Column(db.Integer)

    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), primary_key=True, unique=True)
    message = db.relationship('Message')

    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    recipient = db.relationship('User', backref='message_notifications')

    def __repr__(self):
        return f"id: {self.id} recipient: {self.recipient} message: {self.message}"


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
    chat = db.relationship('Chat', backref='messages')

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', backref='messages')

    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"id: {self.id}, sender_id: {self.sender_id}, content: {self.content}"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'sender': self.user.serialize,
            'content': self.content,
            'is_read': self.is_read,
            'date': [self.date.strftime("%Y:%M:%D:%H:%M"), self.date.strftime("%H:%M")]
        }
