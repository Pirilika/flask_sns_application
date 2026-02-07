from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import login_user, logout_user, login_required

from flaskr import db
from flaskr.models import (
    User, PasswordResetToken
)
from flaskr.forms import (
    LoginForm, RegisterForm, ResetPasswordForm
)
from flaskr.service import (
    UserService, PasswordResetTokenService, TokenNotFoundError
)


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('app.home'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User.select_user_by_email(form.email.data)

        if user and user.is_active and user.validate_password(form.password.data):
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next:
                next = url_for('app.home')
            return redirect(next)
        
        elif not user:
            flash('存在しないユーザーです')
        elif not user.is_active:
            flash('無効なユーザーです。パスワードを再設定してください')
        elif not user.validate_password(form.password.data):
            flash('メールアドレスとパスワードの組み合わせが誤っています')

    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            user = UserService.register(form)
            PasswordResetTokenService.send_password_reset_token(user)
            flash('パスワード設定用のURLを送りしました。ご確認お願いします。')
            return redirect(url_for('app.login'))
        except TokenNotFoundError as e:
            flash('トークンを作成できませんでした')
        except Exception:
            flash("登録に失敗しました")
    
    return render_template('register.html')