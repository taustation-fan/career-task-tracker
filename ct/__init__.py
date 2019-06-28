from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from ct.model import db, Character, Token, TaskReading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/v1/add', methods=['POST'])
def add_entry():
    payload = request.json
    token_str = payload['token']
    station = payload['station']

    token = Token.query.filter_by(token=token_str).one()
    for task, bonus in payload['tasks'].items():
        db.session.add(TaskReading(
            token=token,
            character=token.character,
            station=station,
            task=task,
            bonus=bonus,
        ))
  
    db.session.commit()
    return jsonify({'character': token.character.name})

@app.route('/v1/stations')
def list_stations():
    records = db.session.query(TaskReading.station).distinct().all()
    stations = [r[0] for r in records]
    return jsonify({'data': stations})


if __name__ == '__main__':
    app.run(debug=True)

