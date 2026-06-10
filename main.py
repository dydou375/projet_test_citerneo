import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from sqlmodel import SQLModel, Session, select
from starlette.middleware.sessions import SessionMiddleware

from app.auth import RequiresLogin
from app.database import engine
from app.models import Client, Order, OrderStatus
from app.routes import clients, commandes
from app.routes import auth


def init_db():
    # Crée les tables dans SQLite si elles n'existent pas encore.
    SQLModel.metadata.create_all(engine)


def seed_db():
    with Session(engine) as session:
        existing = session.exec(select(Client)).first()
        if existing:
            return

        clients_data = [
            Client(name="Alice Dupont", email="alice@exemple.fr", phone="0601020304", address="12 rue de la Paix, Paris"),
            Client(name="Bob Martin", email="bob@exemple.fr", phone="0605060708", address="5 avenue Foch, Lyon"),
            Client(name="Claire Leblanc", email="claire@exemple.fr", phone="0609101112", address="8 bd Victor Hugo, Marseille"),
        ]
        session.add_all(clients_data)
        session.commit()

        # refresh() récupère les id auto-générés par SQLite après le commit.
        for c in clients_data:
            session.refresh(c)

        orders = [
            Order(reference="CMD-001", total_amount=149.90, status=OrderStatus.DELIVERED, client_id=clients_data[0].id),
            Order(reference="CMD-002", total_amount=89.50, status=OrderStatus.SHIPPED, client_id=clients_data[0].id),
            Order(reference="CMD-003", total_amount=320.00, status=OrderStatus.CONFIRMED, client_id=clients_data[1].id),
            Order(reference="CMD-004", total_amount=55.00, status=OrderStatus.CREATED, client_id=clients_data[2].id),
        ]
        session.add_all(orders)
        session.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(
    title="Suivi de commandes",
    description="Application de gestion des clients et de leurs commandes.",
    version="1.0.0",
    lifespan=lifespan,
)

# SessionMiddleware stocke la session dans un cookie signé avec la SECRET_KEY.
# En prod, définir une vraie clé aléatoire via la variable d'environnement SECRET_KEY.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
)

# Gestionnaire pour les routes protégées accédées sans être connecté.
@app.exception_handler(RequiresLogin)
async def requires_login_handler(request: Request, _exc: RequiresLogin):
    # Les requêtes HTMX ne suivent pas les redirections HTTP classiques.
    # On utilise l'en-tête HX-Redirect pour lui demander de rediriger la page entière.
    if request.headers.get("HX-Request"):
        response = Response(status_code=200)
        response.headers["HX-Redirect"] = "/login"
        return response
    return RedirectResponse(url="/login", status_code=302)


app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(commandes.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/commandes/")
