from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash
)
from flask_login import login_user, login_required, logout_user


bp = Blueprint('app', __name__, url_prefix='')