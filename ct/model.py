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

class BatchSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    when = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    token_id = db.Column(db.ForeignKey('token.id'), nullable=False)
    token = db.relationship('Token')
    character_id = db.Column(db.ForeignKey('character.id'), nullable=False)
    character = db.relationship('Character')
    career = db.Column(db.String(140), nullable=False)
    rank = db.Column(db.String(140), nullable=False)
    station = db.Column(db.String(250), nullable=False)

class CareerTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    career = db.Column(db.String(250))

class TaskReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_submission_id = db.Column(db.ForeignKey('batch_submission.id'), nullable=False)
    batch_submission = db.relationship('BatchSubmission', backref=db.backref('readings', lazy=True))
    career_task_id = db.Column(db.ForeignKey('career_task.id'), nullable=False)
    career_task = db.relationship('CareerTask', backref='readings')
    bonus = db.Column(db.Float(), nullable=False)
