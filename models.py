from datetime import datetime

from flask_login import UserMixin

from app import db

chat_participation = db.Table(
    'chat_participation',
    db.Column(
        'chat_id',
        db.Integer,
        db.ForeignKey('chat.id'),
        primary_key=True
    ),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('user.id'),
        primary_key=True
    )
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.id} {self.login}"

    @property
    def serialize(self):
        return {
            'user_id': self.id,
            'login': self.login
        }


class Chat(db.Model, UserMixin):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    participants = db.relationship(
        'User',
        secondary='chat_participation',
        backref='chats',
    )

    def __repr__(self):
        return f"{self.id}"


class Message(db.Model, UserMixin):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(
        db.Integer,
        db.ForeignKey('chat.id', ondelete='CASCADE'),
        nullable=False
    )
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    text = db.Column(db.Text, nullable=False)
    chat = db.relationship(
        'Chat',
        backref=db.backref('messages', lazy='dynamic')
    )
    sender = db.relationship(
        'User',
        backref=db.backref('messages', lazy='dynamic')
    )
