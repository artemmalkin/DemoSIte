from flask import render_template, request
from flask_login import login_required

from blueprints.chat import chat
from forms import TypeMessageForm, SearchForm
from models import User, Chat, Chat_member


@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    forms = dict()
    forms.update(type_message_form=TypeMessageForm(request.form), search_form=SearchForm(request.form))
    if request.method == 'GET':
        if request.args.get('act') == 'new_chat':
            search = str(SearchForm(request.form).search)
            return search

    return render_template('chat.html', chats=Chat.query.all(), users=User.query.all(), **forms)
