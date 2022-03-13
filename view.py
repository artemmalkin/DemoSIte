from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user

from app import app
from forms import RegisterOrLoginForm
from methods import handle_request
from models import User


@app.errorhandler(404)
def http_error_handler(e):
    e = "Страница не найдена."
    return render_template('error.html', error=e, users=User.query.all()), 404


@app.errorhandler(401)
def http_error_handler(e):
    flash("Для доступа к данной странице вы должны быть авторизованы.")
    return redirect(url_for('login'))


@app.route('/')
def index():
    return handle_request(render_template('index.html', users=User.query.all()))


@app.route('/register', methods=['GET', 'POST'])
def register():
    context = dict()

    if current_user.is_anonymous:
        form = RegisterOrLoginForm(request.form)

        if request.method == 'POST' and form.validate_on_register():
            return redirect(url_for('index'))
        else:
            context.update(form=form, users=User.query.all())
            return render_template('register.html', **context)
    else:
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    context = dict()

    if current_user.is_anonymous:
        form = RegisterOrLoginForm(request.form)

        if request.method == 'POST' and form.validate_on_login():
            return redirect(url_for('index'))
        else:
            context.update(form=form, users=User.query.all())
            return render_template('login.html', **context)
    else:
        return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('login'))


@app.route('/profile/<int:user_id>')
def profile(user_id: int):
    return handle_request(render_template('profile.html', user=User.query.get_or_404(user_id), users=User.query.all()))
