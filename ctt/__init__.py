import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from ctt.model import db, Character, Token, CareerTask, BatchSubmission, TaskReading

def make_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ.get('CTT_DB', '/tmp/test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    CORS(app)
    return app

app = make_app()

@app.route('/v1/add', methods=['POST'])
def add_entry():
    payload = request.get_json(force=True)
    missing_attrs = [a for a in ('token', 'station', 'career', 'rank', 'tasks') if not payload.get(a)]
    if missing_attrs:
        return jsonify({'recorded': False, 'missing': missing_attrs})

    token_str = payload['token']
    station = payload['station']

    token = Token.query.filter_by(token=token_str).one()
    batch = BatchSubmission(
        token=token,
        character=token.character,
        station=station,
        career=payload['career'],
        rank=payload['rank'],
    )
    db.session.add(batch)

    for task, bonus in payload['tasks'].items():
        career_task = CareerTask.query.filter_by(name=task).first()
        if career_task is None:
            career_task = CareerTask(
                name=task,
                career=payload['career'],
            )
            db.session.add(career_task)
            
        db.session.add(TaskReading(
            batch_submission=batch,
            career_task=career_task,
            bonus=bonus,
        ))
  
    db.session.commit()
    return jsonify({'character': token.character.name, 'recorded': True})

@app.route('/v1/stations')
def list_stations():
    records = db.session.query(BatchSubmission.station).distinct().all()
    stations = [r[0] for r in records]
    return jsonify({'data': stations})

@app.route('/v1/stats-by-character')
def stats_by_player():
    results = db.session.query(Character.name, func.count(BatchSubmission.id)) \
              .join(Character).group_by(Character.name).all()
    by_player = {}
    for r in results:
        by_player[r[0]] = r[1]
    return jsonify({'data': by_player})

if __name__ == '__main__':
    app.run(debug=True)

