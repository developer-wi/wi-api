import datetime

from sqlalchemy import Column, Integer, String

from databaselib.mysql.app import Base
from redis_om.model import JsonModel, EmbeddedJsonModel, Field
from redis_om import get_redis_connection

REDIS_DATA_URL = "redis://:skssk@127.0.0.1:6389"


class Auth(Base):
    __tablename__ = "auth"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(128), unique=True, index=True)
    name = Column(String(128), index=True)
    email = Column(String(128), unique=True, index=True)
    key = Column(String(128))


class CacheAuth(JsonModel):
    id: str = Field(index=True)
    uuid: str
    token: str = Field(index=True, full_text_search=True)
    join_at: datetime.datetime

    class Meta:
        global_key_prefix = "auth"
        model_key_prefix = "raw-auth"
        database = get_redis_connection(url=REDIS_DATA_URL, decode_responses=True)
