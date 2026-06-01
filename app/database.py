from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import create_engine

# Chemin vers le fichier SQLite. Les 3 slashes signifient "chemin relatif".
DATABASE_URL = "sqlite:///database.db"


# SQLite désactive les clés étrangères par défaut.
# Ce listener s'exécute à chaque nouvelle connexion pour les forcer à ON,
# ce qui permet notamment la suppression en cascade (client → ses commandes).
@event.listens_for(Engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = create_engine(
    DATABASE_URL,
    # FastAPI est multi-thread : on désactive la restriction SQLite
    # qui interdit d'utiliser une connexion depuis plusieurs threads.
    connect_args={"check_same_thread": False},
)
