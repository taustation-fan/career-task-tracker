import os
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from ctt.model import db, Character, Token, CareerTask, BatchSubmission, TaskReading

def make_app():
    app = Flask(__name__)
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ.get('CTT_DB', '/tmp/test.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ctt'
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
    if 'Confined to the' in station or 'Doing activity' in station:
        return jsonify({'recorded': False, 'message': '{} does not look like a valid station name'.format(station)})
    batch = BatchSubmission(
        token=token,
        character=token.character,
        station=station,
        career=payload['career'],
        rank=payload['rank'],
    )
    db.session.add(batch)

    response = {'character': token.character.name}

    factors = []

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
            
        tr = TaskReading(
            batch_submission=batch,
            career_task=career_task,
            bonus=bonus,
        )
        db.session.add(tr)
        factors.append(tr.factor)
    factor = max(factors);
    batch.factor = factor
    if factor:
        print('Recorded factor {} for station {}, {}'.format(factor, station, datetime.now()))

    response['recorded'] = True
    response['factor'] = factor
    factors = {}
    if ', ' in station:
        local_station, system = station.split(', ', 2)
        date_limit = datetime.now() - timedelta(hours=6)
        stations = db.session.query(BatchSubmission.station).filter(
            BatchSubmission.station.like('%, ' + system),
            BatchSubmission.when >= date_limit,
        ).distinct()
        for st, in stations.all():
            if st == station:
                continue
            bs = BatchSubmission.query.filter_by(station=st).order_by(BatchSubmission.when.desc()).first()
            factor = max(o.factor for o in bs.readings)
            st = st.split(', ')[0]
            factors[st] = factor
    if factors:
        response['system_factors'] = factors
  
    db.session.commit()

    return jsonify(response)

@app.route('/v1/summary')
def summary():
    token_str = request.args.get('token')
    assert token_str, 'Missing token'
    token = Token.query.filter_by(token=token_str).first()
    assert token, 'Invalid token'
    assert token.full_read_permission, 'Permission denied'

    stations = db.session.query(BatchSubmission.station).filter(BatchSubmission.factor != None).order_by(BatchSubmission.station).distinct()

    factors = defaultdict(dict) # factors = {'YC Ceti': {'Cape Verde Stronghold': 1.25}}

    for station, in stations:
        bs = BatchSubmission.query.filter_by(station=station).filter(BatchSubmission.factor != None).order_by(BatchSubmission.when.desc()).first()
        if not bs:
            continue
        if (datetime.now() - bs.when).total_seconds() > 6 * 3600:
            continue
        local_station, system = bs.station.split(', ')
        system = system.replace(' system', '')
        factors[system][local_station] = bs.factor

    result = ''
    for system in sorted(factors.keys()):
        for station in sorted(factors[system].keys()):
            factor = factors[system][station]
            result += '{:.2f}  {:20} {:30}\n'.format(factor, system, station)

    return Response(result, mimetype='text/plain')
            

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
        result = delta.total_seconds() > 6 * 3600

    return jsonify({'needs_update': result})

if __name__ == '__main__':
    app.run(debug=True)

