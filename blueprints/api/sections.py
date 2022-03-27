from typing import Union, Any

from flask import render_template
from flask_login import current_user
from werkzeug.datastructures import MultiDict

from blueprints.api.errors import Error
from blueprints.chat.tools import chat_or_none, set_chat_read
from models import ChatParticipation, Message, User


class Section:
    """
        Base class for defining sections.

        Section - group of api methods.
    """

    def __init__(self, args: MultiDict[str, str], method_dict: dict):
        self.method = method_dict
        self.args = args


class Messages(Section):
    """
        For working with database of messages
    """

    def __init__(self, args: MultiDict[str, str]):
        method_dict = {
            "get": self.get,
            "search": self.search
        }
        super().__init__(args, method_dict)

    def get(self) -> dict:
        page: int = self.args.get('p', default=1, type=int)
        recipient_id: int = self.args.get('user_id', type=int)

        prt = ChatParticipation.query.filter_by(sender_id=current_user.id, recipient_id=recipient_id).one_or_none()
        if prt:
            messages = Message.query.filter_by(chat_id=prt.chat.id).order_by(Message.id.desc()).paginate(
                page, 15, False)
            return {'messages': [x.serialize for x in messages.items]}
        else:
            return {'error': Error.UserNotFound}

    def search(self) -> Union[list[Any], Any]:
        user_id: int = self.args.get('user_id', type=int)
        content: str = self.args.get('content')

        if content:
            prt = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                    recipient_id=user_id).one_or_none()
            if prt is not None:
                messages = Message.query.filter(Message.chat_id == prt.chat.id,
                                                Message.content.ilike('%' + content + '%')).all()
                return [message.serialize for message in messages]
            else:
                return {'error': Error.UserNotFound}
        return {'error': Error.InvalidRequest}


class Users(Section):
    """
        For working with database of users
    """

    def __init__(self, args: MultiDict[str, str]):
        method_dict = {
            "chat_id": self.chat_id,
            "search": self.search
        }
        super().__init__(args, method_dict)

    def chat_id(self) -> dict:
        user_id: int = self.args.get('user_id', type=int)

        chat = chat_or_none(user_id)
        if chat:
            chat_id = chat.id
            set_chat_read(chat_id)
            return {'chat_id': chat_id}
        else:
            return {'error': Error.UserNotFound}

    def search(self) -> str:
        username: str = self.args.get('username')
        page: int = self.args.get('p', default=1, type=int)

        users = None
        if username:
            users = User.query.filter(User.login.ilike('%' + username + '%'),
                                      User.login != current_user.login).order_by(User.id.desc()).paginate(page, 5,
                                                                                                          False)
        return render_template('user-list.html', page=page, users=users)


class Chats(Section):
    """
        For working with database of chats
    """

    def __init__(self, args: MultiDict[str, str]):
        method_dict = {
            "get": self.get
        }
        super().__init__(args, method_dict)

    @staticmethod
    def get() -> dict:
        return {'chats': [chat.serialize for chat in current_user.chats]}


class Notifications(Section):
    """
        For working with database of notifications
    """

    def __init__(self, args: MultiDict[str, str]):
        method_dict = {
            "get": self.get,
            "count": self.count
        }
        super().__init__(args, method_dict)

    @staticmethod
    def get() -> str:
        message_notifications = Message.query.filter(Message.recipient_id == current_user.id,
                                                     Message.is_read == False).count()

        return render_template('notification-list.html', msg_notifications=message_notifications)

    @staticmethod
    def count() -> int:
        message_notifications = Message.query.filter(Message.recipient_id == current_user.id,
                                                     Message.is_read == False)
        return message_notifications.count() + len(current_user.notifications)
