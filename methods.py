import sqlalchemy
from flask import render_template, request
from flask_login import current_user

from blueprints.chat.tools import remove_chat_notification, create_chat
from forms import TypeMessageForm
from models import User, ChatParticipation, Chat


def if_get_request(template):
    if request.args:
        for key in request.args.keys():
            if key in methods:
                return methods[key](req=request.args.get(key))
            else:
                return template
    return template


class ChatMethods:

    def search_user(req: str, result=''):
        if req:
            result = User.query.filter(User.login.contains(req))
            result = [x.serialize for x in result.all() if x.id != current_user.id] if result.all() else ''
        return render_template('user-list.html', result=result)

    def chat(req: int):
        context = dict()

        try:
            recipient = User.query.get(int(req))
            if recipient.id == current_user.id:
                raise ValueError

        except ValueError:
            recipient = None

        context.update(recipient=recipient)

        try:
            chat_id = ChatParticipation.query.filter_by(recipient_id=recipient.id,
                                                        sender_id=current_user.id).one().chat_id
            current_chat = Chat.query.filter_by(id=chat_id).one()

            context.update(current_chat=current_chat)

            remove_chat_notification(chat_id)
        except UnboundLocalError:
            pass
        except AttributeError:
            pass
        except sqlalchemy.exc.NoResultFound:
            context.update(current_chat=create_chat(data={'recipient': recipient.id}))

        context.update(users=User.query.all(),
                       type_message_form=TypeMessageForm(request.form))

        return render_template('chat.html', **context)


def get_notifications(req):
    return render_template('notification-list.html')


methods = {
    "q": ChatMethods.search_user,
    "c": ChatMethods.chat,
    "ntfs": get_notifications
}
