from sqlalchemy.ext.declarative import declarative_base

DATABASE_PATH = 'databases/database.db'
Base = declarative_base()

from pyeng.database.tables import Class, Task, ClassTask,\
    UnconfUser, User, StudentsTask, Auth
from pyeng.database.db import Database
