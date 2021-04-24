from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_PATH = 'databases/database.db'
Base = declarative_base()

from pyeng.database.tables import Class, Task, ClassTask,\
    UnconfUser, User, StudentsTask, Auth

engine = create_engine('sqlite:///' + DATABASE_PATH)
Session = sessionmaker(bind=engine)
