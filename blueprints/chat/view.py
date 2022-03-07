from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room

from app import socketio
from blueprints.chat import chat
from blueprints.chat.tools import create_chat, add_message, new_chat_notification
from blueprints.chat.methods import methods
from forms import TypeMessageForm
from models import User, Chat, ChatParticipation


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
def on_join():
    room = session['_user_id']
    join_room(room)


@socketio.on('leave')
def on_leave(data):
    leave_room(data)


@socketio.on('send_message')
def handle_message(data):
    chat_id = ChatParticipation.query.filter_by(recipient_id=data['recipient'],
                                                sender_id=current_user.id).one().chat_id
    message = add_message(chat=Chat.query.filter_by(id=chat_id).one(), content=data['content'])
    message['chat_id'] = chat_id
    emit('received_message', message, room=session['_user_id'])
    emit('received_message', message, room=str(data['recipient']))


@socketio.on('new_chat')
def new_chat(data):
    create_chat(data)


@socketio.on('new_notification')
def notification_handler(data):
    print('new notification', data)
    recipient_id = ChatParticipation.query.filter_by(sender_id=data['sender']['id'],
                                                     chat_id=data['chat_id']).one().recipient_id
    print(new_chat_notification(user=User.query.filter_by(id=recipient_id).one(),
                                title=f"Сообщение от {data['sender']['login']}",
                                content=data['content']))
