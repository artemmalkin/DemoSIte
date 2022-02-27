from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room
from sqlalchemy.exc import SQLAlchemyError

from app import socketio, db
from blueprints.chat import chat
from blueprints.chat.templates.methods import methods
from forms import TypeMessageForm
from models import User

@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    context = dict()
    if request.args:
        for key in request.args.keys():
            if key in methods:
                return methods[key](req=request.args.get(key))
            else:
                context.update(users=User.query.all(),
                               type_message_form=TypeMessageForm(request.form))
                return render_template('chat.html', **context)
    else:
        context.update(users=User.query.all(), type_message_form=TypeMessageForm(request.form))
        return render_template('chat.html', **context)


@socketio.on('send_message')
def handle_message(message):
    room = session.get('room')
    message['from'] = {'login': current_user.login, 'id': current_user.id}
    emit('recieved_message', message, room=room)


@socketio.on('join')
def on_join(data):
    print(data)
    username = current_user.login
    session['username'] = username
    session['chat_id'] = 1
    room = session.get('chat_id')
    join_room(room)

@socketio.on('new_chat')
def new_chat(data):
    print(Chat.participants)
    try:
        db.session.add_all([Chat(), Chat.participants.append(User.query.filter_by(id=current_user.id))])
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e.__dict__['orig'])
        print(error)
