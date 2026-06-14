from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///database.db"


# SQLite désactive les clés étrangères par défaut — sans ça le CASCADE ne fonctionne pas
@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # FastAPI est multi-thread, SQLite ne l'est pas par défaut
)


def get_session():
    with Session(engine) as session:
        yield session
