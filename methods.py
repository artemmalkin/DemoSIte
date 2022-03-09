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
                return methods[key](data=request.args)
            else:
                return template
    return template


class ChatMethods:

    def search_user(data):
        response = None
        if data.get('q'):
            response = User.query.filter(User.login.contains(data.get('q')))
            response = [x.serialize for x in response.all() if x.id != current_user.id] if response.all() else ''
        return render_template('user-list.html', result=response)

    def chat(data):
        context = dict()

        try:
            recipient = User.query.get(int(data.get('c')))
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

    def get_messages(data):
        response = None

        try:
            count = int(data.get('m'))
            messages = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                         recipient_id=int(data.get('r_id'))).one().chat.messages[
                       -count:-count + 50]
            message_list = [x.serialize for x in messages]
            response = {'data': {'me': current_user.id}, 'messages': message_list}
        except ValueError:
            pass

        return response


def get_notifications(data):
    return render_template('notification-list.html')


methods = {
    "q": ChatMethods.search_user,
    "c": ChatMethods.chat,
    "m": ChatMethods.get_messages,
    "ntfs": get_notifications
}
