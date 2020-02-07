from amazons import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    game = db.relationship('Game', backref='player', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Game(db.Model):  # many to many with User
    id = db.Column(db.Integer, primary_key=True)
    white_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    black_user_id = db.Column(db.Integer)
    result = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow )


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

