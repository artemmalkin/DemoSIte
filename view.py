from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.security import generate_password_hash

from app import app, db
from forms import RegisterForm, LoginForm
from models import User


@app.errorhandler(404)
def http_error_handler(e):
    e = "Страница не найдена."
    return render_template('error.html', error=e), 404


@app.errorhandler(401)
def http_error_handler(e):
    flash("Для доступа к данной странице вы должны быть авторизованы.")
    return redirect(url_for('login'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    context = dict()

    if current_user.is_anonymous:
        form = RegisterForm(request.form)

        if request.method == 'POST' and form.validate():
            user = User(login=form.data['login'],
                        password=generate_password_hash(form.data['password']))

            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            context.update(form=form)
            return render_template('register.html', **context)
    else:
        return redirect(url_for('index'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    context = dict()
    if current_user.is_anonymous:
        form = LoginForm(request.form)

        if request.method == 'POST' and form.validate():
            login_user(form.get_user(), remember=True)
            return redirect(url_for('index'))
        else:
            context.update(form=form)
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
    return render_template('profile.html', user=User.query.get_or_404(user_id))
