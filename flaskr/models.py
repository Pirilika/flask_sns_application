from flaskr import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from datetime import timedelta, datetime
from uuid import uuid4


class User(UserMixin, db.Model):
    pass