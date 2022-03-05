from flask import render_template, request, session
from flask_login import current_user
from flask_socketio import emit, join_room

from app import socketio
from forms import TypeMessageForm
from models import User, Chat, ChatParticipation


def search_user(req, result=''):
    if req:
        result = User.query.filter(User.login.contains(req))
        result = [x.serialize for x in result.all()] if result.all() else ''
    return render_template('user-list.html', result=result)


def chat(req: int):
    context = dict()

    try:
        recipient = User.query.get(int(req))
        context.update(recipient=recipient)
    except ValueError:
        pass
    try:
        chat_id = ChatParticipation.query.filter_by(recipient_id=recipient.id,
                                                    sender_id=current_user.id).one().chat_id
        current_chat = Chat.query.filter_by(id=chat_id).one()

        context.update(current_chat=current_chat)
    except UnboundLocalError:
        pass
    except AttributeError:
        pass

    context.update(chats=User.query.filter_by(id=current_user.id).one().chats,
                   users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form))
    return render_template('chat.html', **context)


methods = {
    "q": search_user,
    "c": chat,
}
