import sqlalchemy
from flask import render_template, request
from flask_login import current_user

from blueprints.chat.tools import create_chat, set_chat_read
from forms import TypeMessageForm
from models import User, ChatParticipation, Chat


def handle_request(template):
    """
    Parse requests from the client and return response back

    Example:
        @app.route('/')

        def index():
            return handle_request(render_template('index.html'))

    :param template: (render_template function) if no response is found - return that
    :return: template or response
    """
    for key in request.args.keys():
        if key in methods:
            return methods[key](request.args)
    return template


def search_user(data):
    # TODO загрузка по номеру страницы
    response = None
    page = 1

    if data.get('q'):
        try:
            page = int(data.get('page'))
        except ValueError:
            pass
        response = User.query.filter(User.login.contains(data.get('q')), User.login != current_user.login).paginate(
            page, 10, False)

    return render_template('user-list.html', response=response)


def set_current_chat(data):
    context = dict()
    current_chat = None
    recipient = None

    try:
        recipient = User.query.get_or_404(int(data.get('c')))
        if recipient.id == current_user.id:
            raise ValueError

        chat_id = ChatParticipation.query.filter_by(recipient_id=recipient.id,
                                                    sender_id=current_user.id).one().chat_id
        chat = Chat.query.filter_by(id=chat_id).one()
        current_chat = chat

        set_chat_read(chat_id)
    except ValueError:
        pass
    except sqlalchemy.exc.NoResultFound:
        current_chat = create_chat(data={'recipient': recipient.id})

    context.update(users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form),
                   current_chat=current_chat,
                   current_recipient=recipient)

    return render_template('chat.html', **context)


def get_messages(data):
    response = None

    try:
        count = int(data.get('m'))
        messages = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                     recipient_id=int(data.get('r_id'))).one().chat.messages[
                   -count:-count + 50]
        message_list = [x.serialize for x in messages]
        response = {'data': {'me': current_user.id}, 'messages': message_list}
    except ValueError:
        pass

    return response


def get_notifications(data):
    # TODO загрузка по номеру страницы
    return render_template('notification-list.html')


methods = {
    "q": search_user,
    "c": set_current_chat,
    "m": get_messages,
    "ntfs": get_notifications
}
