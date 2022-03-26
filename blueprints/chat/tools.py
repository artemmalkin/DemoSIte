from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import User, Chat, ChatParticipation, Message, Notification


def chat_or_none(recipient_id):
    chat = None

    if recipient_id != current_user.id:
        chat_participation = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                               recipient_id=recipient_id).one_or_none()
        if chat_participation:
            chat = chat_participation.chat
        else:
            recipient = User.query.filter_by(id=recipient_id).one_or_none()

            if recipient:
                new_chat = Chat()

                new_chat.users_participation.append(
                    ChatParticipation(sender=current_user, recipient_id=recipient.id))
                new_chat.users_participation.append(
                    ChatParticipation(sender=recipient, recipient_id=current_user.id))

                db.session.add(new_chat)
                db.session.commit()

                chat = new_chat

    return chat


def add_message(chat_id, recipient_id, content):
    message = None

    try:
        message = Message(chat_id=chat_id, sender=current_user, recipient_id=recipient_id, content=content)
        db.session.add(message)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)

    return message.serialize


def set_chat_read(chat_id):
    Message.query.filter(Message.chat_id == chat_id, Message.sender_id != current_user.id).update(
        {Message.is_read: True})
    db.session.commit()


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
