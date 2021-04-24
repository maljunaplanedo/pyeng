from pyeng.database import Database


def create_database():
    db = Database.get_db()
    db.create_all()
