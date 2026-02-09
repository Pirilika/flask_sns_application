from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import login_user, logout_user, login_required

from flaskr.forms import (
    LoginForm, RegisterForm, ResetPasswordForm, ForgotPasswordForm
)
from flaskr.service import (
    UserService, UserNotFoundError,
    PasswordResetTokenService, InactiveUserError, InvalidPasswordError, TokenNotFoundError,
    PasswordResetService, InvalidResetToken,
    ForgotPasswordService
)


bp = Blueprint('app', __name__, url_prefix='')

# ここから直接modelsとdbにアクセスしないようにする
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
        try:
            user = UserService.login_flow(form.email.data, form.password.data)
            login_user(user, remember=True)

            next_url = request.args.get('next') or url_for('app.home')
            return redirect(next_url)
        
        except UserNotFoundError:
            flash('存在しないユーザーです')
        except InactiveUserError:
            flash('無効なユーザーです。パスワードを再設定してください')
        except InvalidPasswordError:
            flash('メールアドレスとパスワードの組み合わせが誤っています')

    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            user = UserService.register(form.username.data, form.email.data)
            PasswordResetTokenService.send_password_reset_token(user)
            flash('パスワード設定用のURLを送りしました。ご確認お願いします。')
            return redirect(url_for('app.login'))
        except TokenNotFoundError as e:
            flash('トークンを作成できませんでした')
        except Exception as e:
            flash("登録に失敗しました")
    
    return render_template('register.html', form=form)


@bp.route('/reset_password/<uuid:token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        token = str(token)
        form = ResetPasswordForm(request.form)
        user = PasswordResetService.get_user(token)
    except InvalidResetToken as e:
        print(e)
        abort(404)

    if request.method == 'POST' and form.validate():
        try:
            PasswordResetService.set_new_password(user, form.password.data, token)
            flash('パスワードを更新しました')
            return redirect(url_for('app.login'))
            
        except Exception:
            flash('更新に失敗しました')

    return render_template('reset_password.html', form=form)


@bp.route('forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            ForgotPasswordService.send_password_reset_token(form.email.data)
            flash('パスワード再登録用のURLを発行しました')
            return render_template('app.login')
        except TokenNotFoundError as e:
            print(e)
            flash('トークンを作成できませんでした')
        except Exception as e:
            print(e)
            flash("登録に失敗しました")

    return render_template('forgot_password.html', form=form)