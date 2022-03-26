import re

from flask import render_template, request, session
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room

from app import socketio
from blueprints.chat import chat
from blueprints.chat.tools import add_message, set_chat_read
from forms import TypeMessageForm
from models import ChatParticipation


@chat.route('/')
@login_required
def index():
    context = dict()
    context.update(type_message_form=TypeMessageForm(request.form))
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
    prt = ChatParticipation.query.filter(ChatParticipation.recipient_id == data['recipient'],
                                         ChatParticipation.sender_id == current_user.id).one_or_none()
    if len(re.sub("^\s+|\n|\r|\s+$", '', data['content'])) != 0 and prt is not None:
        message = add_message(chat_id=prt.chat_id, recipient_id=data['recipient'],
                              content=data['content'])
        message['chat_id'] = prt.chat_id

        # Send the message to both users
        emit('received_message', message, room=session['_user_id'])
        emit('received_message', message, room=str(data['recipient']))


@socketio.on('chat is read')
def chat_is_read(data):
    set_chat_read(data['chat_id'])
