from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import create_engine

DATABASE_URL = "sqlite:///database.db"


@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)