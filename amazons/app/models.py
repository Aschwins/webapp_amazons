from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(80), index=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    game = db.relationship('Game', backref='user', lazy='dynamic')
    player = db.relationship('Player', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def __repr__(self):
        return f'<Player {self.user_id}>'


class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    move_type = db.Column(db.String(40))
    move_order = db.Column(db.Integer)
    move_notation = db.Column(db.String(80))
    from_position = db.Column(db.String(20))
    to_position = db.Column(db.String(20))


class Game(db.Model):  # many to many with User
    id = db.Column(db.Integer, primary_key=True)
    user_started_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    player = db.relationship('Player', backref='game', lazy='dynamic')

    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))

    def __repr__(self):
        return '<Game %r>' % self.id


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(20))

    game = db.relationship('Game', backref='result', lazy='dynamic')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

