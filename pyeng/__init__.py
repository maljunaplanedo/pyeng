from flask import Flask


def create_app():
    app = Flask(__name__)
    with app.app_context():
        from pyeng import views
    return app


INVITE_CODE_LEN = 8
AUTH_HASH_LEN = 32
AUTH_HASH_COOKIE_LIFESPAN = 60 * 60 * 24 * 365 * 10
TASK1_FULL_WORD_BONUS = 100
TASK1_WRONG_LETTER_FINE = 30