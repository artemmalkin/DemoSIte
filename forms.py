from wtforms import Form, StringField, PasswordField, validators, TextAreaField, SearchField, SubmitField


class RegisterOrLoginForm(Form):
    login = StringField('Логин', [validators.Length(min=4, max=15)])
    password = PasswordField('Пароль', [validators.Length(min=8, max=50)])
class SearchForm(Form):
    search = SearchField(render_kw={"placeholder": "Поиск"})

class TypeMessageForm(Form):
    message = TextAreaField(render_kw={"placeholder": "Ваше сообщение"})
    attach_button = SubmitField('Прикрепить', render_kw={"class": "button"})
    send_button = SubmitField('Отправить', render_kw={"class": "button"})
