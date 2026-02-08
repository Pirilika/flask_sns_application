from flask import flash

from flaskr import db
from models import User, PasswordResetToken

# 認証エラー
class AuthenticationError(Exception):
    pass

class UserNotFoundError(AuthenticationError):
    pass

class InactiveUserError(AuthenticationError):
    pass

class InvalidPasswordError(AuthenticationError):
    pass


# トークンエラー
class TokenNotFoundError(Exception):
    pass

class InvalidResetToken(Exception):
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
    
    @classmethod
    def login_flow(cls, email, password):
        user = User.find_by_email(email)

        if not user:
            raise UserNotFoundError()
        
        if not user.is_active:
            raise InactiveUserError()
        
        if not user.validate_password(password):
            raise InvalidPasswordError()
        
        return user
    

class PasswordResetTokenService():
    @classmethod
    def send_password_reset_token(cls, user):
        token = None
        with db.session.begin():
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
    

class PasswordResetService():
    @classmethod
    def get_user(cls, token):
        #? 結合は大がかりかも
        user_id = PasswordResetToken.get_user_id_by_token(token) #? 見つからないとき例外を出す処理をmodelに記述してもおK？
        if user_id:
            user = User.find_by_id(user_id)
            return user
        else:
            raise InvalidResetToken

    @classmethod
    def set_new_password(cls, user, password, token):
        with db.session.begin():
            user.save_new_password(password)
            PasswordResetToken.delete_token(token)
