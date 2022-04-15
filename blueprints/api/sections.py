from typing import Union, Any

from flask import render_template, url_for
from flask_login import current_user
from werkzeug.datastructures import MultiDict

from app import db
from blueprints.api.errors import Error
from blueprints.chat.tools import chat_or_none, set_chat_read
from models import ChatParticipation, Message, User, Notification


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
            return {'has_next': messages.has_next, 'messages': [x.serialize for x in messages.items]}
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
            "search": self.search
        }
        super().__init__(args, method_dict)

    def search(self) -> str:
        username: str = self.args.get('username')
        page: int = self.args.get('p', default=1, type=int)

        context = dict()

        if username:
            pagination = User.query.filter(User.login.ilike('%' + username + '%'),
                                           User.login != current_user.login).order_by(User.id.desc()).paginate(page, 5,
                                                                                                               False)
            context.update(pagination=pagination, getFunc='getUsers', page=page)

        return render_template('user-list.html', **context)


class Chats(Section):
    """
        For working with database of chats
    """

    def __init__(self, args: MultiDict[str, str]):
        method_dict = {
            "get_list": self.get_list,
            "get_chat": self.get_chat
        }
        super().__init__(args, method_dict)

    def get_chat(self) -> dict:
        user_id: int = self.args.get('user_id', type=int)

        chat = chat_or_none(user_id)
        if chat:
            chat_id = chat.id
            set_chat_read(chat_id)
            return {'chat_id': chat_id, 'recipient_login': User.query.get(user_id).login}
        else:
            return {'error': Error.UserNotFound}

    @staticmethod
    def get_list() -> dict:
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

    def get(self) -> dict:
        page: int = self.args.get('p', type=int)

        response = {}

        def ntf_handle(ntf):
            ntf_json = ntf.serialize
            ntf.is_read = True
            return ntf_json

        chat_ntf_count = Message.query.filter(Message.recipient_id == current_user.id,
                                              Message.is_read == False).count()

        if page:
            pagination = Notification.query.filter(Notification.user_id == current_user.id).order_by(
                Notification.id.desc()).paginate(page, 20, False)
            ntfs = pagination.items
            response.update(pagination=render_template('pagination.html',
                                                       page=page,
                                                       pagination=pagination,
                                                       getFunc='getNotifications'))
        else:
            ntfs = Notification.query.filter(Notification.user_id == current_user.id).order_by(
                Notification.id.desc()).limit(5)

        base_ntf = [ntf_handle(x) for x in ntfs]
        db.session.commit()

        response.update(base_ntf=base_ntf, chat_ntf_count=chat_ntf_count, see_more=url_for('notifications'))
        return response

    @staticmethod
    def count() -> int:
        message_notifications = Message.query.filter(Message.recipient_id == current_user.id,
                                                     Message.is_read == False)
        base_ntf = Notification.query.filter(Notification.user_id == current_user.id, Notification.is_read == False)
        return message_notifications.count() + base_ntf.count()
