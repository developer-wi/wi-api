from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_MASTER_DATABASE_URL = (
    "mysql+pymysql://test.id:aaaa@127.0.0.1:13306/test_project"
)
SQLALCHEMY_SLAVE_DATABASE_URL = (
    "mysql+pymysql://test.id:aaaa@127.0.0.1:13307/test_project"
)

master_engine = create_engine(
    SQLALCHEMY_MASTER_DATABASE_URL,
    pool_size=5,
    max_overflow=0,
    pool_recycle=3600,
    pool_pre_ping=True,
)

slave_engine = create_engine(
    SQLALCHEMY_SLAVE_DATABASE_URL,
    pool_size=5,
    max_overflow=0,
    pool_recycle=3600,
    pool_pre_ping=True,
)

Master_Session = sessionmaker(autocommit=False, autoflush=False, bind=master_engine)

Slave_Session = sessionmaker(autocommit=False, autoflush=False, bind=slave_engine)

Master_Base = declarative_base()
