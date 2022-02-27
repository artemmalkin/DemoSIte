from datetime import datetime

from flask_login import UserMixin

from app import db

chat_participation = db.Table(
    'chat_participation',
    db.Column(
        'chat_id',
        db.Integer,
        db.ForeignKey('chats.id'),
        primary_key=True
    ),
    db.Column(
        'user_id',
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )
)


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
            'user_id': self.id,
            'login': self.login
        }


class Chat(db.Model, UserMixin):
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', backref='chats', secondary=chat_participation)

    def __repr__(self):
        return f"{self.id}"


class Message(db.Model, UserMixin):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    chat = db.relationship('Chat', backref='messages')

    def __repr__(self):
        return f"id: {self.id}, sender_id: {self.sender_id}, content: {self.content}"

# ouruser = User(login='test', password='123')
# ourchat = Chat()
# ouruser.chats.append(ourchat)
# db.session.add(ouruser)
# db.session.commit()
# ourchat.messages.append(Message(content='contentik', is_read=False, sender_id=ouruser.id))
# db.session.add(ourchat)
# db.session.commit()
