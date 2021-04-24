from pyeng.database import Base, engine
from pyeng.database import Class, Task, ClassTask,\
    UnconfUser, User, StudentsTask, Auth
from flask import request
from pyeng.database import Session as DBSession


def create_database():
    Base.metadata.create_all(engine)


def create_teachers_account(name, surname):
    pass


def get_client(db):
    if 'auth_hash' not in request.cookies:
        return None

    auth_hash = request.cookies.get('auth_hash')

    auth = db.query(Auth).filter(Auth.auth_hash == auth_hash).first()
    client = db.query(User).filter(User.id == auth.user_id).first()

    return client


def check_client_type(client, *allowed):
    return User.get_type(client) in allowed


def check_class_name(name):
    return isinstance(name, str) and len(name) > 0


def check_name(name):
    return isinstance(name, str) and len(name) > 0 and ' ' not in name
