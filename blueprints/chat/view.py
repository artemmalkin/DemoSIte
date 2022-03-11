from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room

from app import socketio
from blueprints.chat import chat
from blueprints.chat.tools import create_chat, add_message, new_chat_notification, set_chat_read
from forms import TypeMessageForm
from methods import handle_request
from models import User, ChatParticipation, Message


@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    context = dict()
    context.update(users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form))
    return handle_request(render_template('chat.html', **context))


@socketio.on('join')
def on_join():
    room = session['_user_id']
    join_room(room)


@socketio.on('leave')
def on_leave(data):
    leave_room(data)


@socketio.on('send_message')
def handle_message(data):
    current_chat = ChatParticipation.query.filter_by(recipient_id=data['recipient'],
                                                     sender_id=current_user.id).one().chat

    message = add_message(chat=current_chat, content=data['content'])
    message['chat_id'] = current_chat.id

    # Send the message to both users
    emit('received_message', message, room=session['_user_id'])
    emit('received_message', message, room=str(data['recipient']))

    # Send the notification to recipient
    new_chat_notification(recipient=User.query.filter_by(id=data['recipient']).one(),
                          message=Message.query.filter_by(id=message['id']).one())


@socketio.on('chat is read')
def chat_is_read(data):
    set_chat_read(data['chat_id'])


@socketio.on('new_chat')
def new_chat(data):
    create_chat(data)
