from sqlalchemy import Column, Integer, String

from database.app import Master_Base, master_engine


class User(Master_Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), index=True)
    email = Column(String(128), unique=True, index=True)
    key = Column(String(128))


Master_Base.metadata.create_all(bind=master_engine)
