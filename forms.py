from flask import flash
from werkzeug.security import check_password_hash
from wtforms import Form, StringField, PasswordField, validators, TextAreaField, SubmitField

from models import User


class RegisterForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15), validators.input_required()])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50), validators.input_required()])
    confirm_password = PasswordField('Подтвердите пароль', [validators.input_required()])

    def validate_login(self, field):
        if User.query.filter(User.login == self.data['login']).count() > 0:
            flash('Логин уже зарегистрирован.')
            raise validators.ValidationError('Duplicate username')

    def validate_confirm_password(self, field):
        if field.data != self.data['password']:
            flash('Пароли не совпадают.')
            raise validators.ValidationError('Passwords do not match')

    def get_user(self):
        return User.query.filter(User.login == self.data['login']).one_or_none()


class LoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15), validators.input_required()])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50), validators.input_required()])

    def validate_login(self, field):
        user = User.query.filter(User.login == self.data['login']).one_or_none()

        if user:
            if not check_password_hash(user.password, self.data['password']):
                flash('Неправильный пароль.')
                raise validators.ValidationError('Invalid Password')

    def get_user(self):
        return User.query.filter(User.login == self.data['login']).one_or_none()


class TypeMessageForm(Form):
    input_message = TextAreaField(render_kw={"placeholder": "Ваше сообщение"})
    send_button = SubmitField('Отправить', render_kw={"class": "button"})
