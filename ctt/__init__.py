from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from ctt.model import db, Character, Token, CareerTask, BatchSubmission, TaskReading

def make_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    CORS(app)
    return app

app = make_app()

@app.route('/v1/add', methods=['POST'])
def add_entry():
    payload = request.get_json(force=True)
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
    return jsonify({'character': token.character.name})

@app.route('/v1/stations')
def list_stations():
    records = db.session.query(BatchSubmission.station).distinct().all()
    stations = [r[0] for r in records]
    return jsonify({'data': stations})


if __name__ == '__main__':
    app.run(debug=True)

