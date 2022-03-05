from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, send, leave_room
from sqlalchemy.exc import SQLAlchemyError

from app import socketio, db
from blueprints.chat import chat
from blueprints.chat.methods import methods
from forms import TypeMessageForm
from models import User, Chat, ChatParticipation, Message


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


@socketio.on('join')
def on_join(data):
    if 'chat' in session:
        emit('leave', data=session['room'])
    room = data['chat']
    join_room(room)
    session['room'] = room
    print(session)


@socketio.on('leave')
def on_leave(data):
    print('leave')
    leave_room(data)


@socketio.on('send_message')
def handle_message(data):
    room = ChatParticipation.query.filter_by(recipient_id=data['recipient'],
                                             sender_id=current_user.id).one().chat_id
    data['sender'] = current_user.serialize
    try:
        current_chat = Chat.query.filter_by(id=room).one()
        sender = User.query.filter_by(id=current_user.id).one()
        current_chat.messages.append(Message(user=sender, content=data['content']))
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)
    emit('received_message', data, room=str(room))


@socketio.on('new_chat')
def create_chat(data: int):
    try:
        sender = User.query.filter_by(id=current_user.id).one()
        recipient = User.query.filter_by(id=data['recipient']).one()

        for sender_chat in sender.chats:
            if recipient in sender_chat.users:
                raise SQLAlchemyError('This chat already exists.')

        new_chat = Chat()

        new_chat.user_participations.append(ChatParticipation(user=sender, recipient_id=data['recipient']))
        new_chat.user_participations.append(ChatParticipation(user=recipient, recipient_id=current_user.id))

        db.session.add_all([new_chat])
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)
