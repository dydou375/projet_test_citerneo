from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlmodel import SQLModel, Session, select

from app.database import engine
from app.models import Client, Order, OrderStatus
from app.routes import clients, commandes


def init_db():
    SQLModel.metadata.create_all(engine)


def seed_db():
    with Session(engine) as session:
        existing = session.exec(select(Client)).first()
        if existing:
            return

        clients = [
            Client(name="Alice Dupont", email="alice@exemple.fr", phone="0601020304", address="12 rue de la Paix, Paris"),
            Client(name="Bob Martin", email="bob@exemple.fr", phone="0605060708", address="5 avenue Foch, Lyon"),
            Client(name="Claire Leblanc", email="claire@exemple.fr", phone="0609101112", address="8 bd Victor Hugo, Marseille"),
        ]
        session.add_all(clients)
        session.commit()
        for c in clients:
            session.refresh(c)

        orders = [
            Order(reference="CMD-001", total_amount=149.90, status=OrderStatus.DELIVERED, client_id=clients[0].id),
            Order(reference="CMD-002", total_amount=89.50, status=OrderStatus.SHIPPED, client_id=clients[0].id),
            Order(reference="CMD-003", total_amount=320.00, status=OrderStatus.CONFIRMED, client_id=clients[1].id),
            Order(reference="CMD-004", total_amount=55.00, status=OrderStatus.CREATED, client_id=clients[2].id),
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

app.include_router(clients.router)
app.include_router(commandes.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/commandes/")
