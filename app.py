from datetime import datetime


from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost/users?client_encoding=utf8'
app.config['SECRET_KEY'] = 'SAD12DJJ34KDds#sdsda'


db = SQLAlchemy(app)
migrate = Migrate(app, db)


login_manager = LoginManager(app)

# variable of current user for current session
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

# DB MODEL
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<user id{self.id}:{self.login}>"

# WTFORMS
class RegisterForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=25)])
    password = PasswordField('Пароль')

class LoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=25)])
    password = PasswordField('Пароль')

# HANDLERS
@app.route('/')
def index():
    if current_user.is_authenticated:
        login = str(current_user.login)
    return render_template('index.html', users=User.query.all(), login=login)

@app.route('/register', methods=['GET', 'POST'])
def signup():
    form = RegisterForm(request.form)
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

    return render_template('register.html', form=form, users=User.query.all())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    print(form)
    if request.method == 'POST':
        user = db.session.query(User).filter(User.login == form.login.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=False)
            return redirect(url_for('index'))
        flash("Неверный логин или пароль")
        return redirect(url_for('login'))
    return render_template('login.html', form=form, users=User.query.all())


if __name__ == '__main__':
    app.run(debug=True)
