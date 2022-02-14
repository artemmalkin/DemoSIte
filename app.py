from datetime import datetime

import flask_login
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, UserMixin, login_required, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, validators

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/users?client_encoding=utf8'
app.config['SECRET_KEY'] = 'SAD12DJJ34KDds#sdsda'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.id} {self.login}"


class RegisterOrLoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15)])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50)])


@app.errorhandler(Exception)
def http_error_handler(e):
    # context = dict()
    # login = ''
    # if current_user.is_authenticated:
    #     login = current_user.login
    # context.update(error=e, login=login, users=User.query.all())
    # -------------------------------------------
    # Ты можешь прямо в html вызвать current_user и current_user.login
    return render_template('error.html', error=e, users=User.query.all())


@app.route('/')
def index():
    # context = dict()
    # login = ''
    # if current_user.is_authenticated:
    #     login = current_user.login
    # context.update(login=login, )
    # -------------------------------------------
    # Ты можешь прямо в html вызвать current_user и current_user.login
    return render_template('index.html', users=User.query.all())


@app.route('/chat')
@login_required
def chat():
    # context = dict()
    # login = current_user.login
    # context.update(login=login, users=User.query.all())
    # return render_template('chat.html', **context)
    # -------------------------------------------
    # Ты можешь прямо в html вызвать current_user и current_user.login
    return render_template('chat.html', users=User.query.all())


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
    return render_template('profile.html', user=User.query.get_or_404(user_id))


if __name__ == '__main__':
    app.run(debug=True)
