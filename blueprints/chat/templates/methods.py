from flask import render_template, request

from forms import TypeMessageForm
from models import User, Chat


def search_user(req, result=''):
    if req:
        result = User.query.filter(User.login.contains(req))
        result = [x.serialize for x in result.all()] if result.all() else ''
    return render_template('user-list.html', result=result)


def chat(req):
    context = dict()
    try:
        current_chat = User.query.get(int(req))
        context.update(current_chat=current_chat)
    except ValueError:
        pass
    context.update(chats=Chat.query.all(), users=User.query.all(), type_message_form=TypeMessageForm(request.form))
    return render_template('chat.html', **context)


methods = {
    "q": search_user,
    "c": chat,
}
