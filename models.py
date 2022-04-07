from datetime import datetime

from flask_security import RoleMixin, UserMixin, current_user

from app import db, login_manager

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


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
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary=roles_users, backref='users')

    def __repr__(self):
        return f"id: {self.id} login: {self.login}"

    def is_active(self):
        return True

    @property
    def is_has_access(self):
        # Check access for flask-admin
        return any(True for r in self.roles if r in ['admin', 'supervisor', 'user', 'create', 'read'])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'login': self.login
        }


@login_manager.user_loader
def load_user(user_id):
    # Load User model in current_user
    return User.query.get(user_id)


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


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


class Chat(db.Model, UserMixin):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True)

    users = db.relationship('User', backref='chats', secondary='chat_participation', viewonly=True)

    def __repr__(self):
        return f"{self.id}"

    @property
    def serialize(self):
        data = {'recipient': recipient for recipient in self.users if recipient != current_user}
        notifications = Message.query.filter(Message.chat_id == self.id, Message.recipient_id == current_user.id,
                                             Message.is_read == False).count()

        return {
            'id': self.id,
            'recipient': {'id': data['recipient'].id, 'login': data['recipient'].login},
            'notifications': notifications
        }


class Message(db.Model, UserMixin):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)

    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    chat = db.relationship('Chat', backref='messages')

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender = db.relationship('User', backref='messages')

    recipient_id = db.Column(db.Integer, nullable=False)

    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"id: {self.id}, sender_id: {self.sender_id}, content: {self.content}"

    @property
    def serialize(self):
        return {
            'id': self.id,
            'sender': self.sender.serialize,
            'content': self.content,
            'is_read': self.is_read,
            'date': self.date.strftime("%m/%d/%Y") + ' ' + self.date.strftime("%H:%M") + ' UTC'
        }
