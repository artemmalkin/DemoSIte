from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import User, Chat, ChatParticipation, Message


def create_chat(data):
    new_chat = None
    try:
        sender = User.query.filter_by(id=current_user.id).one()
        recipient = User.query.filter_by(id=data['recipient']).one()

        for sender_chat in sender.chats:
            if recipient in sender_chat.users:
                raise SQLAlchemyError('This chat already exists.')

        new_chat = Chat()
        new_chat.user_participations.append(ChatParticipation(user=sender, recipient_id=data['recipient']))
        new_chat.user_participations.append(ChatParticipation(user=recipient, recipient_id=current_user.id))

        db.session.add(new_chat)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)

    return new_chat


def add_message(chat, content):
    message = None
    try:
        sender = User.query.filter_by(id=current_user.id).one()
        message = Message(user=sender, content=content)
        chat.messages.append(message)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)

    return message.serialize
