from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit
from sqlalchemy.exc import SQLAlchemyError

from app import socketio, db
from blueprints.chat import chat
from blueprints.chat.methods import methods
from forms import TypeMessageForm
from models import User, Chat


@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    context = dict()
    context.update(users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form),
                   chats=User.query.filter_by(id=current_user.id).one().chats)
    if request.args:
        for key in request.args.keys():
            if key in methods:
                return methods[key](req=request.args.get(key))
            else:
                return render_template('chat.html', **context)
    else:
        return render_template('chat.html', **context)


@socketio.on('send_message')
def handle_message(message):
    # TODO room == chat.id
    room = session.get('room')
    message['from'] = {'login': current_user.login, 'id': current_user.id}
    emit('recieved_message', message, room=room)


@socketio.on('new_chat')
def new_chat(data: int):
    try:
        new_chat = Chat()

        sender = User.query.filter_by(id=current_user.id).one()
        recipient = User.query.filter_by(id=data['recipient']).one()

        for sender_chat in sender.chats:
            if recipient in sender_chat.users:
                raise SQLAlchemyError('This chat already exists.')

        sender.chats.append(new_chat)
        recipient.chats.append(new_chat)

        db.session.add_all([new_chat, sender, recipient])
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)
