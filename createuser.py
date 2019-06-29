import secrets
import sys

from ct import app, db, Character, Token

name = sys.argv[1]

with app.app_context():
    db.create_all()
    character = Character(name=name)
    db.session.add(character)

    try:
        token_str = sys.argv[2]
    except IndexError:
        token_str = secrets.token_hex()
    token = Token(character=character, token=token_str)
    db.session.add(token)
    db.session.commit()

    print('{} - {}'.format(name, token_str))
