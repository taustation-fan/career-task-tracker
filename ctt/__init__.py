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
        message = 'Missing attributes: '  + ', '.join(missing_attrs)
        return jsonify({'recorded': False, 'missing': missing_attrs, message: message})

    token_str = payload['token']
    station = payload['station']

    token = Token.query.filter_by(token=token_str).first()
    if token is None:
        return jsonify({'recorded': False, 'message': 'Invalid token'})
    batch = BatchSubmission(
        token=token,
        character=token.character,
        station=station,
        career=payload['career'],
        rank=payload['rank'],
    )
    db.session.add(batch)

    for task, bonus in payload['tasks'].items():
        bonus = float(bonus)
        career_task = CareerTask.query.filter_by(name=task).first()
        if career_task is None:
            career_task = CareerTask(
                name=task,
                career=payload['career'],
                bonus_baseline=bonus,
            )
            db.session.add(career_task)
        elif career_task.bonus_baseline is None or career_task.bonus_baseline > bonus:
            career_task.bonus_baseline = bonus
            
        db.session.add(TaskReading(
            batch_submission=batch,
            career_task=career_task,
            bonus=bonus,
        ))
  
    db.session.commit()
    return jsonify({'character': token.character.name, 'recorded': True})

@app.route('/v1/stations')
def list_stations():
    records = db.session.query(BatchSubmission.station).order_by(BatchSubmission.station).distinct().all()
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

@app.route('/v1/station-needs-update/<station>')
def station_needs_update(station):
    newest = BatchSubmission.query.filter_by(station=station) \
             .order_by(BatchSubmission.when.desc()).first()
    
    if newest is None:
        result = True
    else:
        delta = datetime.now() - newest.when
        print(delta)
        result = delta.total_seconds() > 6 * 3600

    return jsonify({'needs_update': result})

if __name__ == '__main__':
    app.run(debug=True)

