from datetime import datetime

from flask import url_for, request, abort
from flask_admin import helpers
from flask_admin.contrib import sqla
from flask_login import UserMixin, current_user
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.utils import redirect

from app import db, login_manager, admin, app


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

    @property
    def serialize(self):
        return {
            'id': self.id,
            'login': self.login
        }

    def get_id(self):
        return self.id


class Role(db.Model, UserMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"id: {self.id} name: {self.name}"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


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
            'date': [self.date.strftime("%Y:%M:%D:%H:%M"), self.date.strftime("%H:%M")]
        }


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


class CustomModelView(sqla.ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.login == 'grklakg':
                return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


class RoleView(CustomModelView):
    can_create = True


class UserView(CustomModelView):
    column_exclude_list = ['password']
    can_create = False
    column_searchable_list = ['login']
    column_editable_list = ['login']


class NotificationView(CustomModelView):
    can_create = True


admin.add_view(RoleView(Role, db.session, name='Роли'))
admin.add_view(UserView(User, db.session, name='Пользователи'))
admin.add_view(NotificationView(Notification, db.session, name='Уведомления'))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=helpers,
        get_url=url_for
    )