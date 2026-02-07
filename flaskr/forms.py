from wtforms.form import Form
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from flaskr.models import User


class LoginForm(Form):
    email = StringField(
        'メール: ' ,
        validators=[
            DataRequired(),
            Email()
        ]
    )
    password = PasswordField(
        'パスワード: ',
        validators=[
            DataRequired(),
            EqualTo('confirm_password', message='パスワードが一致しません')
        ]
    )
    confirm_password = PasswordField(
        'パスワード再入力: ',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(
        'ログイン',
    )


class RegisterForm(Form):
    email = StringField(
        'メール: ',
        validators=[
            DataRequired(),
            Email('メールアドレスが誤っています')
        ]
    )
    username = StringField(
        '名前: ',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(
        '登録',
    )

    def validate_email(self, field):
        if User.select_user_by_email(field.data):
            raise ValidationError('このメールアドレスは既に登録されています')
        

class ResetPasswordForm(Form):
    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(),
            EqualTo('confirm_password', message='パスワードが一致しません'),
        ]
    )
    confirm_password = PasswordField(
        'パスワード確認: ',
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField(
        'パスワードを更新する'
    )

    def validate_password(self, field):
        if len(field.data) < 8:
            raise ValidationError('パスワードは8文字以上である必要があります')