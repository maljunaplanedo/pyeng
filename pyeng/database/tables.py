from pyeng.database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, backref
import time


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

    class_ = relationship('Class', backref=backref('class_tasks', order_by='ClassTask.add_time.desc()',
                                                   cascade="all, delete-orphan"))
    task = relationship('Task', backref=backref('class_tasks', order_by='ClassTask.add_time.desc()',
                                                cascade="all, delete-orphan"))

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

    class_ = relationship('Class', backref=backref("unconf_students", cascade="all, delete-orphan"))

    def __init__(self, code, name, surname, type_, class_):
        self.code = code
        self.name = name
        self.surname = surname
        self.type = type_
        if class_ is not None:
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

    class_ = relationship('Class', backref=backref('students', cascade="all, delete-orphan"))

    def __init__(self, login, password, name, surname, type_, class_):
        self.login = login
        self.password = password
        self.name = name
        self.surname = surname
        self.type = type_
        if class_ is not None:
            self.class_ = class_

    def get_running_task(self):
        for students_task in self.students_tasks:
            if students_task.status == StudentsTask.RUNNING_STATUS:
                return students_task
        return None

    @classmethod
    def get_type(cls, user):
        return cls.GUEST_TYPE if user is None else user.type


class StudentsTask(Base):
    __tablename__ = 'students_tasks'

    NOT_STARTED_STATUS = 0
    RUNNING_STATUS = 1
    FINISHED_STATUS = 2

    id = Column(Integer, primary_key=True, autoincrement=True)
    class_task_id = Column(Integer, ForeignKey('class_tasks.id'))
    task_id = Column(Integer, ForeignKey('tasks.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Integer, default=NOT_STARTED_STATUS)
    result = Column(Integer, default=0)
    answers = Column(Text, default='')
    begin_time = Column(Integer, default=-1)
    add_time = Column(Integer, nullable=False)

    class_task = relationship('ClassTask', backref=backref('students_tasks', order_by='StudentsTask.add_time.desc()',
                                                           cascade="all, delete-orphan"))
    task = relationship('Task', backref=backref('students_tasks', order_by='StudentsTask.add_time.desc()',
                                                cascade="all, delete-orphan"))
    student = relationship('User', backref=backref('students_tasks', order_by='StudentsTask.add_time.desc()',
                                                   cascade="all, delete-orphan"))

    def __init__(self, add_time, class_task, task, student):
        self.add_time = add_time
        self.class_task = class_task
        self.task = task
        self.student = student

    def update_time(self):
        if self.status == self.NOT_STARTED_STATUS:
            return int(2e9)
        if self.status == self.FINISHED_STATUS:
            return int(-2e9)

        current_time = int(time.time())
        end_time = self.begin_time + self.task.duration
        if current_time > end_time:
            self.status = self.FINISHED_STATUS
        return end_time - current_time


class Auth(Base):
    __tablename__ = 'auths'

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_hash = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', backref=backref('auths', cascade="all, delete-orphan"))

    def __init__(self, auth_hash, user):
        self.auth_hash = auth_hash
        self.user = user
