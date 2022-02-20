from flask import Blueprint

chat = Blueprint('chat', __name__, template_folder='templates', url_prefix='/chat')

import blueprints.chat.view
