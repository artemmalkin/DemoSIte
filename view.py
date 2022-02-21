import flask_login
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app import login_manager, app, db
from forms import RegisterOrLoginForm
from models import User


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except Exception:
        return None


@app.errorhandler(Exception)
def http_error_handler(e):
    return render_template('error.html', error=e, users=User.query.all())


@app.route('/')
def index():
    return render_template('index.html', users=User.query.all())


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
            except SQLAlchemyError as e:
                db.session.rollback()
                error = str(e.__dict__['orig'])
                print(error)
                if "already exists" in error:
                    flash(f"Такой логин уже зарегистрирован, повторите попытку.")
        context.update(form=form, users=User.query.all())
        return render_template('register.html', **context)
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    context = dict()
    if current_user.is_anonymous:
        form = RegisterOrLoginForm(request.form)
        if request.method == 'POST':
            user = db.session.query(User).filter(User.login == form.login.data).first()
            if user and check_password_hash(user.password, form.password.data):
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
    return render_template('profile.html', user=User.query.get_or_404(user_id), users=User.query.all())
