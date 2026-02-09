from flaskr import db
from flaskr.models import User, PasswordResetToken

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
    def register(cls, username, email):
        user = User(
            username = username,
            email = email 
        )
        user.create_new_user()
        db.session.commit()
            
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
        token = PasswordResetToken.publish_token(user)
        db.session.commit()

        if not token:
            raise TokenNotFoundError('トークンを作成できませんでした')

        print(f'パスワード設定用URL: http://127.0.0.1:5000/reset_password/{token}')
        return token 
    

class PasswordResetService():
    @classmethod
    def get_user(cls, token):
        user_id = PasswordResetToken.get_user_id_by_token(token) 
        if not user_id:
            raise InvalidResetToken()
        
        user = User.find_by_id(user_id)
        if not user:
            raise InvalidResetToken()
        
        return user

    @classmethod
    def set_new_password(cls, user, password, token):
        user.save_new_password(password)
        PasswordResetToken.delete_token(token)
        db.session.commit()


class ForgotPasswordService():
    @classmethod
    def send_password_reset_token(cls, email):
        user = User.find_by_email(email)
        PasswordResetTokenService.send_password_reset_token(user)