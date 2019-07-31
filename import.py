import json
import sys
import iso8601

from ctt import app, db, Character, Token, BatchSubmission, CareerTask, TaskReading

to_import = json.load(sys.stdin)

with app.app_context():
    db.create_all()
    for c in to_import['Character']:
        obj = Character(**c)
        db.session.add(obj)
    for c in to_import['Token']:
        obj = Token(**c)
        db.session.add(obj)
    for c in to_import['CareerTask']:
        obj = CareerTask(**c)
        db.session.add(obj)
    for c in to_import['BatchSubmission']:
        c['when'] = iso8601.parse_date(c['when'], default_timezone=None)
        obj = BatchSubmission(**c)
        db.session.add(obj)
    for c in to_import['TaskReading']:
        obj = TaskReading(**c)
        db.session.add(obj)

    db.session.commit()
