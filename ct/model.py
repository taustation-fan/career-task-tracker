from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    infotext = db.Column(db.String(250))
    character_id = db.Column(db.ForeignKey('character.id'), nullable=False)
    character = db.relationship('Character', backref=db.backref('tokens', lazy=True))

class TaskReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    when = db.Column(db.DateTime, nullable=False, default=datetime.now)
    token_id = db.Column(db.ForeignKey('token.id'), nullable=False)
    token = db.relationship('Token')
    character_id = db.Column(db.ForeignKey('character.id'), nullable=False)
    character = db.relationship('Character')
    station = db.Column(db.String(250), nullable=False)
    task = db.Column(db.String(250), nullable=False)
    bonus = db.Column(db.Float, nullable=False)
