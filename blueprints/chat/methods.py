import sqlalchemy.exc
from flask import render_template, request
from flask_login import current_user

from blueprints.chat.tools import create_chat
from forms import TypeMessageForm
from models import User, Chat, ChatParticipation


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
    except UnboundLocalError:
        pass
    except AttributeError:
        pass
    except sqlalchemy.exc.NoResultFound:
        context.update(current_chat=create_chat(data={'recipient': recipient.id}))

    context.update(chats=User.query.filter_by(id=current_user.id).one().chats,
                   users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form))

    return render_template('chat.html', **context)


methods = {
    "q": search_user,
    "c": chat,
}
