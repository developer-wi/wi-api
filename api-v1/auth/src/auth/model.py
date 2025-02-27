from sqlalchemy import Column, Integer, String

from database.app import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(128), unique=True, index=True)
    name = Column(String(128), index=True)
    email = Column(String(128), unique=True, index=True)
    key = Column(String(128))
