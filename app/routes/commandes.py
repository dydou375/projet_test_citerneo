from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlmodel import Session, select

from app.config import templates
from app.database import engine
from app.models import Client, Order, OrderStatus
from app.schemas import OrderCreate

router = APIRouter(prefix="/commandes", tags=["Commandes"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/", response_class=HTMLResponse)
def list_orders(request: Request, session: Session = Depends(get_session)):
    orders = session.exec(select(Order)).all()
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(
        "commandes/index.html",
        {"request": request, "orders": orders, "clients": clients, "statuses": OrderStatus},
    )


@router.post("/", response_class=HTMLResponse)
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

    orders = session.exec(select(Order)).all()
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(
        "commandes/_list.html",
        {"request": request, "orders": orders, "clients": clients, "statuses": OrderStatus},
    )


@router.patch("/{order_id}/statut", response_class=HTMLResponse)
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

    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)

    return templates.TemplateResponse(
        "commandes/_row.html",
        {"request": request, "order": order, "statuses": OrderStatus},
    )
