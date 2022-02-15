from wtforms import Form, StringField, PasswordField, validators

class RegisterOrLoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15)])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50)])