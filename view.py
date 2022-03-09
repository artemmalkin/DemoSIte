import flask_login
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import login_manager, app, db
from forms import RegisterOrLoginForm
from methods import if_get_request
from models import User


@login_manager.user_loader # TODO: Это чё за хуйне?
def load_user(user_id): # TODO: Это чё за хуйне?
    try:# TODO: Это чё за хуйне?
        return User.query.get(user_id)# TODO: Это чё за хуйне?
    except Exception:# TODO: Это чё за хуйне?
        return None# TODO: Это чё за хуйне?


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
    return if_get_request(render_template('index.html', users=User.query.all()))


@app.route('/register', methods=['GET', 'POST'])
def signup():
    context = dict()
    if current_user.is_anonymous:
        form = RegisterOrLoginForm(request.form)
        if request.method == 'POST':
            try:
                db.session.add(User(login=request.form.get('login'),
                                    password=generate_password_hash(request.form.get('password'))))
                db.session.commit()
                flash("Вы успешно зарегистрировались!")
            except SQLAlchemyError as e: # TODO: ты wtforms по рофлу используешь?
                db.session.rollback() # TODO: ты wtforms по рофлу используешь?
                error = str(e.__dict__['orig']) # TODO: ты wtforms по рофлу используешь?
                print(error) # TODO: ты wtforms по рофлу используешь?
                if "already exists" in error: # TODO: ты wtforms по рофлу используешь?
                    flash(f"Такой логин уже зарегистрирован, повторите попытку.") # TODO: ты wtforms по рофлу используешь?
        context.update(form=form, users=User.query.all())
        return render_template('register.html', **context)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():# TODO: функция в целом пздц
    context = dict()
    if current_user.is_anonymous:
        form = RegisterOrLoginForm(request.form)
        if request.method == 'POST':
            user = db.session.query(User).filter(User.login == form.login.data).first()
            if user and check_password_hash(user.password, form.password.data): # TODO: ты wtforms по рофлу используешь?
                login_user(user, remember=False)
                return redirect(url_for('index'))
            flash("Неверный логин или пароль")
            return redirect(url_for('login'))
        context.update(form=form, users=User.query.all())
        return render_template('login.html', **context)
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    flask_login.logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('login'))


@app.route('/profile/<int:user_id>')
def profile(user_id: int):
    return if_get_request(render_template('profile.html', user=User.query.get_or_404(user_id), users=User.query.all()))
