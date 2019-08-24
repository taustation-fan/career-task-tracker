from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

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
    full_read_permission = db.Column(db.Boolean(), nullable=False, default=False)

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
    factor = db.Column(db.Float())

class CareerTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    career = db.Column(db.String(250))
    bonus_baseline = db.Column(db.Float())

class TaskReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_submission_id = db.Column(db.ForeignKey('batch_submission.id'), nullable=False)
    batch_submission = db.relationship('BatchSubmission', backref=db.backref('readings', lazy=True))
    career_task_id = db.Column(db.ForeignKey('career_task.id'), nullable=False)
    career_task = db.relationship('CareerTask', backref='readings')
    bonus = db.Column(db.Float(), nullable=False)

    @property
    def factor(self):
        baseline = self.career_task.bonus_baseline
        if baseline is None:
            baseline = db.session.query(func.min(TaskReading.bonus)).filter_by(career_task_id=self.career_task_id).first()
            if baseline is None:
                return None
            baseline = baseline[0]
            self.career_task.bonus_baseline = baseline
            db.session.add(self.career_task)

        return self.bonus / baseline
