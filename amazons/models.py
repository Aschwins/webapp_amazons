from amazons import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    games = db.relationship('Games', backref='player', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username


class Games(db.Model):  # many to many with User
    id = db.Column(db.Integer, primary_key=True)
    white_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    black_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow )
