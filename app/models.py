from . import db
from datetime import datetime, timedelta, timezone
import string
import random
from werkzeug.security import generate_password_hash, check_password_hash

class Url(db.Model):
    '''
    Модель для сокращения URL.
    '''
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    clicks = db.Column(db.Integer, default=0)

    def __init__(self, original_url, days_to_expire=1):
        self.original_url = original_url
        self.short_code = self.generate_short_code()
        self.expires_at = datetime.now(timezone.utc) + timedelta(days=days_to_expire)

    def generate_short_code(self, length=7):
        characters = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(characters) for _ in range(length))
            if not Url.query.filter_by(short_code=short_code).first():
                return short_code

    def __repr__(self):
        return f'<Url {self.short_code}>'


class User(db.Model):
    '''
    Модель для пользователей.
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
