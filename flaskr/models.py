import os

from flaskr import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, select

from datetime import timedelta, datetime, timezone
from uuid import uuid4


class User(UserMixin, db.Model): # サイトだとなんかDeclaraticeBaseのドキュメントのほうが多い
    
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64)) 
    email: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password: Mapped[str] = mapped_column(
        String(128),
        nullable=True
    )
    picture_path: Mapped[str] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, unique=False, default=False)
    create_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
        )
    update_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
        )

    @classmethod
    def select_user_by_email(cls, email):
        stmt = db.select(cls).where(cls.email == email)
        return db.session.scalar(stmt)
    
    @classmethod
    def select_user_by_id(cls, id):
        return db.session.get(User, id)
    
    def validate_password(self, password):
        return check_password_hash(self.password, password)

    def create_new_user(self):
        db.session.add(self)

    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    expire_at: Mapped[datetime] = mapped_column(DateTime)     
    create_at: Mapped[datetime] = mapped_column(DateTime)

    def __init__(self, user_id):
        self.user_id = user_id
        # token生成はここでのみ行う。二重生成には気を付ける。
        self.token = str(uuid4())

        now_time = datetime.now(timezone.utc)
        self.create_at = now_time
        self.expire_at = now_time + timedelta(days=1)

    @classmethod
    def publish_token(cls, user):
        new_token = cls(user.id) 
        db.session.add(new_token)
        db.session.commit()
        return new_token.token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        stmt = db.select(cls).where(cls.token == token)
        record = db.session.execute(stmt).scalar_one_or_none()

        if record is None:
            return None

        if record.expire_at <= datetime.now(timezone.utc):
            cls.delete_token(token)
            return None
        
        return record.user_id
        
    @classmethod
    def delete_token(cls, token):
        stmt = db.select(cls).where(cls.token == token)
        del_token = db.session.execute(stmt).scalar_one_or_none()
        db.session.delete(del_token)
        