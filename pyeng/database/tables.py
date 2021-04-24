from pyeng.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship


class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    given = Column(Text)
    answer = Column(Text)
    duration = Column(Integer, nullable=False)

    def __init__(self, type, name, given, answer, duration):
        self.type = type
        self.name = name
        self.given = given
        self.answer = answer
        self.duration = duration


class ClassTask(Base):
    __tablename__ = 'class_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey('classes.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    add_time = Column(Integer, nullable=False)

    class_ = relationship('Class', backref='class_tasks')
    task = relationship('Task', backref='class_tasks')

    def __init__(self, class_, task, add_time):
        self.class_ = class_
        self.task = task
        self.add_time = add_time


class UnconfUser(Base):
    __tablename__ = 'unconf_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, nullable=False, index=True, unique=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))

    class_ = relationship('Class', backref="unconf_students")

    def __init__(self, code, name, surname, type_, class_):
        self.code = code
        self.name = name
        self.surname = surname
        self.type = type_
        self.class_ = class_


class User(Base):
    __tablename__ = 'users'

    GUEST_TYPE = -1
    TEACHER_TYPE = 0
    STUDENT_TYPE = 1

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    type = Column(Integer, nullable=False)
    class_id = Column(Integer, ForeignKey('classes.id'))

    class_ = relationship('Class', backref='students')

    def __init__(self, login, password, name, surname, type_, class_):
        self.login = login
        self.password = password
        self.name = name
        self.surname = surname
        self.type = type_
        self.class_ = class_

    @classmethod
    def get_type(cls, user):
        return cls.GUEST_TYPE if user is None else user.type


class StudentsTask(Base):
    __tablename__ = 'students_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_task_id = Column(Integer, ForeignKey('class_tasks.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Integer, default=0)
    result = Column(Integer, default=0)
    answers = Column(Text, default='')
    begin_time = Column(Integer, default=-1)
    add_time = Column(Integer, nullable=False)

    class_task = relationship('ClassTask', backref="students_tasks")
    task = relationship('Task', backref="students_tasks")
    student = relationship('User', backref="students_tasks")

    def __init__(self, add_time, class_task, task, student):
        self.add_time = add_time
        self.class_task = class_task
        self.task = task
        self.student = student


class Auth(Base):
    __tablename__ = 'auths'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_hash = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', backref='auths')

    def __init__(self, auth_hash, user):
        self.auth_hash = auth_hash
        self.user = user
