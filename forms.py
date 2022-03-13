from flask import flash
from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import Form, StringField, PasswordField, validators, TextAreaField, SubmitField, ValidationError

from app import db
from models import User


class RegisterOrLoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15), validators.input_required()])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50), validators.input_required()])

    def validate_on_register(self):
        user = User.query.filter(User.login == self.data['login']).first()

        if user:
            flash('Логин уже зарегистрирован')
            return False
        else:
            user = User(login=self.data['login'],
                        password=generate_password_hash(self.data['password']))

            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)

            return True

    def validate_on_login(self):
        user = User.query.filter(User.login == self.data['login']).first()

        if user:
            if check_password_hash(user.password, self.data['password']):
                login_user(user, remember=True)
                return True

        flash('Неправильный логин или пароль')
        return False


class TypeMessageForm(Form):
    input_message = TextAreaField(render_kw={"placeholder": "Ваше сообщение"})
    send_button = SubmitField('Отправить', render_kw={"class": "button"})
