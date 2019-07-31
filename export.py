import json

from ctt import app, db, Character, Token, BatchSubmission, CareerTask, TaskReading


def _extract_data(cls):
    result = []
    for obj in cls.query.all():
        copy = dict(**obj.__dict__)
        copy.pop('_sa_instance_state')
        result.append(copy)
    return result


with app.app_context():
    output = {
        'Token':            _extract_data(Token),
        'Character':        _extract_data(Character),
        'BatchSubmission':  _extract_data(BatchSubmission),
        'CareerTask':       _extract_data(CareerTask),
        'TaskReading':      _extract_data(TaskReading),
    }
    print(json.dumps(output, default=str, indent=2, sort_keys=True))
