from typing import Union, Any

from flask import render_template
from flask_login import current_user
from werkzeug.datastructures import MultiDict

from blueprints.api.errors import Error
from blueprints.chat.tools import chat_or_none, set_chat_read
from models import ChatParticipation, Message, User


class Messages:
    def __init__(self, args: MultiDict[str, str]):
        self.method = {
            "get": self.get,
            "search": self.search
        }

        self.args = args

    def get(self) -> dict:
        page = self.args.get('p', default=1, type=int)
        recipient_id = self.args.get('user_id', type=int)
        prt = ChatParticipation.query.filter_by(sender_id=current_user.id, recipient_id=recipient_id).one_or_none()

        if prt:
            chat_id = prt.chat.id

            messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.id.desc()).paginate(
                page, 15, False)

            message_list = [x.serialize for x in messages.items]

            return {'messages': message_list}
        else:
            return {'error': Error.InvalidRequest}

    def search(self) -> Union[list[Any], Any]:
        user_id = self.args.get('user_id', type=int)
        content = self.args.get('content')

        if content:
            prt = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                    recipient_id=user_id).one_or_none()
            if prt is not None:
                result = []
                messages = Message.query.filter(Message.chat_id == prt.chat.id,
                                                Message.content.ilike('%' + content + '%')).all()
                for message in messages:
                    result.append(message.serialize)

                return result
            else:
                return {'error': Error.UserNotFound}
        return {'error': Error.InvalidRequest}


class Users:
    def __init__(self, args: MultiDict[str, str]):
        self.method = {
            "chat_id": self.chat_id,
            "search": self.search
        }

        self.args = args

    def chat_id(self) -> dict:
        user_id = self.args.get('user_id', type=int)

        chat = chat_or_none(user_id)
        if chat:
            chat_id = chat.id
            set_chat_read(chat_id)
            return {'chat_id': chat_id}
        else:
            return {'error': Error.UserNotFound}

    def search(self) -> str:
        username = self.args.get('username')
        page = self.args.get('p', default=1, type=int)

        users = None
        if username:
            users = User.query.filter(User.login.ilike('%' + username + '%'),
                                      User.login != current_user.login).order_by(User.id.desc()).paginate(page, 5,
                                                                                                          False)
        return render_template('user-list.html', page=page, users=users)


class Chats:
    def __init__(self, args: MultiDict[str, str]):
        self.method = {
            "get": self.get
        }

        self.args = args

    @staticmethod
    def get() -> dict:
        chat_list = [chat.serialize for chat in current_user.chats]
        return {'chats': chat_list}


class Notifications:
    def __init__(self, args: MultiDict[str, str]):
        self.method = {
            "get": self.get,
            "count": self.count
        }

        self.args = args

    @staticmethod
    def get() -> Union[dict[str, int], str]:
        message_notifications = Message.query.filter(Message.recipient_id == current_user.id,
                                                     Message.is_read == False).count()

        return render_template('notification-list.html', msg_notifications=message_notifications)

    @staticmethod
    def count():
        message_notifications = Message.query.filter(Message.recipient_id == current_user.id,
                                                     Message.is_read == False).count()
        count = message_notifications + len(current_user.notifications)

        return count
