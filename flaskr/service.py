import glob
import os
from datetime import datetime

from werkzeug.utils import secure_filename
from flask_login import current_user

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


class UpdateUserInfoService():
    @classmethod
    def update_flow(cls, new_username, new_email, new_file_data):
        user_id = current_user.get_id()
        user = User.find_by_id(user_id)

        if not user:
            raise UserNotFoundError
        
        user.username = new_username
        user.email = new_email
        
        if new_file_data and new_file_data.filename:
            cls._updatefile_flow(user, new_file_data)

        db.session.commit()

    @classmethod
    def _updatefile_flow(cls, user, file_data):
        new_path = cls._save_picture_file(user, file_data)
        cls._update_picture_path(user, new_path)

    @classmethod
    def _save_picture_file(cls, user, file_data):
        cls._delete_old_file(user)

        ext = os.path.splitext(secure_filename(file_data.filename))[1]
        file_name = f'{user.id}_{int(datetime.now().timestamp())}.{ext}'

        picture_path = os.path.join('flaskr/static/user_image/', file_name)

        with open(picture_path, 'wb') as f:
            f.write(file_data.read())

        return f'user_image/{file_name}'

    @classmethod
    def _delete_old_file(cls, user):
        base_dir = os.path.join('flaskr/static/user_image')
        prefix = f'{user.id}_'

        pattern = os.path.join(base_dir, f'{prefix}*')

        for path in glob.glob(pattern):
            if os.path.isfile(path):
                os.remove(path)

    @classmethod
    def _update_picture_path(cls, user, new_path):
        user.picture_path = new_path


class ChangePasswordService():
    @classmethod
    def change_password_flow(cls, new_password):
        user = User.find_by_id(current_user.get_id())

        if not user:
            raise UserNotFoundError
        
        user.save_new_password(new_password)
        db.session.commit()
