from flask import render_template, request
from flask_login import current_user
from sqlalchemy import func

from blueprints.chat.tools import get_chat, set_chat_read
from forms import TypeMessageForm
from models import User, ChatParticipation, Message


def handle_request(template):
    """
    Parse requests from the client and return response back

    Example:
        @app.route('/')

        def index():
            return handle_request(render_template('index.html'))

    :param: template: (render_template function) if no response is found - return that
    :return: template or response
    """
    for key in request.args.keys():
        if key in methods:
            return methods[key](request.args)
    return template


def search_user(data):
    response = {'page': 1, 'users': []}
    if data.get('search_user'):
        try:
            response['page'] = int(data.get('p'))
        except ValueError:
            pass

        response['users'] = User.query.filter(User.login.ilike('%' + data.get('search_user') + '%'),
                                              User.login != current_user.login). \
            order_by(User.id.desc()).paginate(response['page'], 5, False)

    return render_template('user-list.html', response=response)


def get_chat_id(data):
    """
    Getting chat_id by recipient id

    if chat is not found - will create a new chat and return his ID

    :return: render_template (with chat_id parameter) or only chat_id (if assigned 'id' key)
    """
    context = dict()
    chat_id = None

    try:
        recipient_id = int(data.get('user'))
        chat = get_chat(recipient_id)
        if chat:
            chat_id = chat.id
            set_chat_read(chat_id)
    except ValueError:
        pass

    # if you need get only chat_id without template
    if 'id' in data.keys():
        return {'chat_id': chat_id}

    context.update(users=User.query.all(),
                   type_message_form=TypeMessageForm(request.form),
                   chat_id=chat_id)
    return render_template('chat.html', **context)


def get_messages(data):
    response = {}

    try:
        page = int(data.get('p'))

        chat_id = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                    recipient_id=int(data.get('r_id'))).one().chat.id

        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.id.desc()).paginate(
            page, 15, False)

        message_list = [x.serialize for x in messages.items]

        response = {'messages': message_list}
    except ValueError:
        pass

    return response


def search_message(data):
    response = {'result': []}

    if data.get('search_message'):
        chat_id = ChatParticipation.query.filter_by(sender_id=current_user.id,
                                                    recipient_id=data.get('user')).one_or_none().chat.id

        messages = Message.query.filter(Message.chat_id == chat_id,
                                        Message.content.ilike('%' + data.get('search_message') + '%')).all()

        for message in messages:
            response['result'].append(message.serialize)

    return response


def get_chats(data):
    chat_list = [chat.serialize for chat in current_user.chats]
    response = {'chats': chat_list}
    return response


def get_notifications(data):
    if data.get('ntfs') == 'count':
        count = len(current_user.message_notifications) + len(current_user.notifications)
        return {'count_of_notifications': count}
    return render_template('notification-list.html')


methods = {
    "search_user": search_user,
    "user": get_chat_id,
    "search_message": search_message,
    "messages": get_messages,
    "dialogs": get_chats,
    "ntfs": get_notifications
}
