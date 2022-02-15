from flask import Blueprint, render_template
from flask_login import login_required
from models import User

chat = Blueprint('chat', __name__, template_folder='templates')


@chat.route('/')
@login_required
def chat():
    return render_template('templates/chat.html', users=User.query.all())