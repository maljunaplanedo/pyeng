from pyeng.database import Base, engine
from pyeng.database import Class, Task, ClassTask,\
    UnconfUser, User, StudentsTask, Auth
from flask import request
from pyeng.database import Session as DBSession
from pyeng import INVITE_CODE_LEN
import random
import string
import time


def create_database():
    Base.metadata.create_all(engine)


def create_teachers_account(name, surname):
    with DBSession() as db:
        teacher = add_unconf_user(db, name, surname, User.TEACHER_TYPE)
        db.commit()
        return teacher.code


def get_client(db):
    if 'auth_hash' not in request.cookies:
        return None

    auth_hash = request.cookies.get('auth_hash')

    auth = db.query(Auth).filter(Auth.auth_hash == auth_hash).first()
    if auth is None:
        return None
    client = db.query(User).filter(User.id == auth.user_id).first()

    return client


def check_client_type(client, *allowed):
    return User.get_type(client) in allowed


def check_class_name(name):
    return isinstance(name, str) and len(name) > 0


def check_name(name):
    return isinstance(name, str) and len(name) > 0 and ' ' not in name


def check_task_name(name):
    return isinstance(name, str) and len(name) > 0


def check_task_given(given):
    return isinstance(given, str) and len(given) > 0


def check_task_answer_format(answer):
    return isinstance(answer, str) and len(answer) > 0


def check_task_duration(duration):
    return isinstance(duration, int) and duration <= 604800


def check_login_format(login):
    return isinstance(login, str) and len(login) > 0


def check_password_format(password):
    return isinstance(password, str) and len(password) > 0


def check_invite_code(invite_code):
    return isinstance(invite_code, str) and len(invite_code) == INVITE_CODE_LEN


def generate_random_string(length):
    return ''.join([random.choice(string.ascii_lowercase) for i in range(length)])


def add_unconf_user(db, name, surname, type_, class_=None):
    invite_code = generate_random_string(INVITE_CODE_LEN)
    unconf_user = UnconfUser(invite_code, name, surname, type_, class_)
    db.add(unconf_user)
    return unconf_user
