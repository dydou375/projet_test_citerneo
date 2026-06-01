from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.config import templates
from app.database import engine
from app.models import Client, Order, OrderStatus
from app.schemas import OrderCreate

router = APIRouter(prefix="/commandes", tags=["Commandes"])


def get_session():# On crée une fonction de dépendance pour obtenir une session de base de données. Cela nous permet de réutiliser ce code dans tous nos endpoints sans avoir à répéter la logique d'ouverture et de fermeture de la session.
    with Session(engine) as session:
        yield session


@router.get("/", response_class=HTMLResponse)# Cet endpoint affiche la liste de toutes les commandes. On récupère également la liste des clients et des statuts pour pouvoir les afficher dans le template.
def list_orders(request: Request, session: Session = Depends(get_session)):
    orders = session.exec(select(Order).options(selectinload(Order.client))).all()
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(
        request, "commandes/index.html",
        {"orders": orders, "clients": clients, "statuses": OrderStatus},
    )


@router.post("/", response_class=HTMLResponse)# Cet endpoint permet de créer une nouvelle commande. Les données sont envoyées via un formulaire, et on utilise Pydantic pour valider ces données avant de les insérer dans la base de données.
def create_order(
    request: Request,
    reference: str = Form(...),
    total_amount: float = Form(...),
    client_id: int = Form(...),
    session: Session = Depends(get_session),
):
    try:
        data = OrderCreate(reference=reference, total_amount=total_amount, client_id=client_id)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not session.get(Client, data.client_id):
        raise HTTPException(status_code=404, detail="Client introuvable")

    order = Order(**data.model_dump())
    session.add(order)
    session.commit()

    orders = session.exec(select(Order).options(selectinload(Order.client))).all()
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(
        request, "commandes/_list.html",
        {"orders": orders, "clients": clients, "statuses": OrderStatus},
    )


@router.patch("/{order_id}/statut", response_class=HTMLResponse) # Cet endpoint permet de mettre à jour le statut d'une commande. Le nouveau statut est envoyé via un formulaire, et on vérifie que ce statut est valide avant de l'enregistrer dans la base de données.
def update_order_status(
    order_id: int,
    request: Request,
    status: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        new_status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=422, detail="Statut invalide")

    order = session.exec(
        select(Order).where(Order.id == order_id).options(selectinload(Order.client))
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)

    return templates.TemplateResponse(
        request, "commandes/_row.html",
        {"order": order, "statuses": OrderStatus},
    )
