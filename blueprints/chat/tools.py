from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import User, Chat, ChatParticipation, Message, Notification, MessageNotification


def get_chat(recipient_id):
    chat = None
    recipient = User.query.filter_by(id=recipient_id).one_or_none()

    if recipient and recipient_id != current_user.id:
        chat_participation = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                               recipient_id=recipient_id).one_or_none()
        if chat_participation:
            chat = chat_participation.chat
        else:
            new_chat = Chat()

            new_chat.users_participation.append(
                ChatParticipation(sender=current_user, recipient_id=recipient.id))
            new_chat.users_participation.append(
                ChatParticipation(sender=recipient, recipient_id=current_user.id))

            db.session.add(new_chat)
            db.session.commit()

            chat = new_chat

    return chat


def add_message(chat, content):
    message = None

    try:
        message = Message(sender=current_user, content=content)
        chat.messages.append(message)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)

    return message.serialize


def new_chat_notification(recipient, message):
    notification = None

    try:
        notification = MessageNotification(message=message, chat_id=message.chat_id)
        recipient.message_notifications.append(notification)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)

    return notification


def set_chat_read(chat_id):
    try:
        MessageNotification.query.filter_by(chat_id=chat_id, recipient_id=current_user.id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)


def new_notification(user, title, content):
    notification = None

    try:
        notification = Notification(title=title, content=content)
        user.notifications.append(notification)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)

    return notification
