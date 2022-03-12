from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import User, Chat, ChatParticipation, Message, Notification, MessageNotification


def create_chat(data):
    new_chat = None
    try:
        sender = User.query.filter_by(id=current_user.id).one()
        recipient = User.query.filter_by(id=data['recipient']).one()

        for sender_chat in sender.chats:
            if recipient in sender_chat.users:
                raise SQLAlchemyError('This chat already exists.')

        new_chat = Chat()
        new_chat.users_participation.append(ChatParticipation(user=sender, recipient_id=data['recipient']))
        new_chat.users_participation.append(ChatParticipation(user=recipient, recipient_id=current_user.id))

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


def new_chat_notification(recipient, message):
    notification = None
    try:
        notification = MessageNotification(message=message, chat_id=message.chat_id)
        recipient.message_notifications.append(notification)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)

    return notification


def set_chat_read(chat_id):
    success = False
    try:
        MessageNotification.query.filter_by(chat_id=chat_id, recipient_id=current_user.id).delete()
        db.session.commit()
        success = True
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)

    return success


def new_notification(user, title, content):
    notification = None
    try:
        notification = Notification(title=title, content=content)
        user.notifications.append(notification)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        error = str(e)
        print(error)

    return notification
