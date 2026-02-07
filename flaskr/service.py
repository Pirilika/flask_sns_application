from flask import flash

from flaskr import db
from models import User, PasswordResetToken


class TokenNotFoundError(Exception):
    pass


class UserService():
    @classmethod
    def register(cls, form):
        user = User(
            username = form.username.data,
            email = form.email.data  
        )

        with db.session.begin():
            user.create_new_user()

        return user
    

class PasswordResetTokenService():
    @classmethod
    def send_password_reset_token(cls, user):
        token = cls._create_token(user)

        if not token:
            raise TokenNotFoundError('トークンを作成できませんでした')

        print(f'パスワード設定用URL: http://127.0.0:5000/reset_password/{token}')
        return token 

    @classmethod
    def _create_token(cls, user):
        with db.session.begin():
            token = PasswordResetToken.publish_token(user)

        return token