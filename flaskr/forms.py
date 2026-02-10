from wtforms.form import Form
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField, HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from flask_login import current_user

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
        if User.find_by_email(field.data):
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
        

class ForgotPasswordForm(Form):
    email = StringField(
        'メール: ',
        validators=[
            DataRequired(), Email()
        ]
    )
    submit = SubmitField(
        'パスワードを再設定する'
    )

    def validate_email(self, field):
        if not User.find_by_email(field.data):
            raise ValidationError('そのメールアドレスは存在しません')
        

class UserForm(Form):
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
    picture_file = FileField(
        'ファイルアップロード',
    )
    submit = SubmitField(
        '登録情報更新'
    )

    def validate_email(self, field):
        user = User.find_by_email(field.data)
        if not user:
            return True
        
        if user.id == int(current_user.get_id()):
            return True
        
        raise ValidationError('そのメールアドレスは既に登録されています')