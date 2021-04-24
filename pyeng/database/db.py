from pyeng.database import DATABASE_PATH
from pyeng.database import Class, Task, ClassTask,\
    UnconfUser, User, StudentsTask, Auth
from pyeng.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    _instance = None

    @classmethod
    def get_db(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def __init__(self):
        if Database._instance is not None:
            raise Exception("Do NOT use the constructor! Use get_db() method!")

        self.engine = create_engine('sqlite:///' + DATABASE_PATH)
        self.Session = sessionmaker(bind=self.engine)
        self.session = None

    def open_session(self):
        self.session = self.Session()

    def close_session(self):
        self.session.commit()
        self.session.close()
