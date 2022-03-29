from flask_login import current_user

from app import db
from models import User, Chat, ChatParticipation, Message, Notification


def chat_or_none(recipient_id: int) -> Chat():
    if recipient_id != current_user.id:
        chat_participation = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                               recipient_id=recipient_id).one_or_none()
        if chat_participation:
            return chat_participation.chat
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
                return new_chat
    return None


def add_message(chat_id: int, recipient_id: int, content: str) -> dict:
    message = Message(chat_id=chat_id, sender=current_user, recipient_id=recipient_id, content=content)
    db.session.add(message)
    db.session.commit()
    return message.serialize


def set_chat_read(chat_id: int) -> None:
    Message.query.filter(Message.chat_id == chat_id, Message.sender_id != current_user.id).update(
        {Message.is_read: True})
    db.session.commit()


def new_notification(user: User, title: str, content: str) -> Notification:
    notification = Notification(title=title, content=content)
    user.notifications.append(notification)
    db.session.commit()
    return notification
