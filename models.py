from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))

class PlayerSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_tag = db.Column(db.String(20), nullable=False)
    player_name = db.Column(db.String(100))
    trophies = db.Column(db.Integer)
    search_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
