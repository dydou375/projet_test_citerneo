import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import ValidationError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth import require_auth
from app.config import templates
from app.database import engine
from app.models import ALLOWED_TRANSITIONS, Client, Order, OrderStatus
from app.schemas import OrderCreate

# dependencies=[Depends(require_auth)] protège toutes les routes de ce router d'un coup.
router = APIRouter(prefix="/commandes", tags=["Commandes"], dependencies=[Depends(require_auth)])


def get_session():
    with Session(engine) as session:
        yield session


def _apply_filters(query, client_id: Optional[str], status: Optional[str]):
    """Applique les filtres client et statut sur une requête SQLModel.
    Les deux paramètres sont des str pour accepter les chaînes vides du formulaire
    (un select non rempli envoie "" qu'on ne peut pas convertir directement en int).
    """
    if client_id:  # "" est falsy → pas de filtre si rien n'est sélectionné
        try:
            query = query.where(Order.client_id == int(client_id))
        except ValueError:
            pass
    if status:
        try:
            query = query.where(Order.status == OrderStatus(status))
        except ValueError:
            pass
    return query


@router.get("/", response_class=HTMLResponse)
def list_orders(
    request: Request,
    # Paramètres de filtre optionnels passés dans l'URL (ex: /commandes/?status=livrée)
    # Optional[str] et non int : le formulaire envoie "" quand rien n'est sélectionné.
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = _apply_filters(select(Order).options(selectinload(Order.client)), client_id, status)
    orders = session.exec(query).all()
    clients = session.exec(select(Client)).all()
    # On convertit client_id en int pour la comparaison dans le template ({% if filter_client_id == client.id %})
    return templates.TemplateResponse(
        request, "commandes/index.html",
        {
            "orders": orders,
            "clients": clients,
            "statuses": OrderStatus,
            "transitions": ALLOWED_TRANSITIONS,
            "filter_client_id": int(client_id) if client_id else None,
            "filter_status": status or None,
        },
    )


@router.get("/export.csv")
def export_csv(
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    # Mêmes filtres que la liste — ce qu'on voit, on l'exporte
    query = _apply_filters(select(Order).options(selectinload(Order.client)), client_id, status)
    orders = session.exec(query).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Référence", "Client", "Montant (€)", "Date", "Statut"])
    for order in orders:
        writer.writerow([
            order.reference,
            order.client.name if order.client else "",
            f"{order.total_amount:.2f}",
            order.created_at.strftime("%d/%m/%Y"),
            order.status.value,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=commandes.csv"},
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

    orders = session.exec(select(Order).options(selectinload(Order.client))).all()
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(
        request, "commandes/_list.html",
        {"orders": orders, "clients": clients, "statuses": OrderStatus, "transitions": ALLOWED_TRANSITIONS},
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

    order = session.exec(
        select(Order).where(Order.id == order_id).options(selectinload(Order.client))
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    if new_status not in ALLOWED_TRANSITIONS[order.status]:
        raise HTTPException(status_code=422, detail="Transition de statut non autorisée")

    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)

    return templates.TemplateResponse(
        request, "commandes/_row.html",
        {"order": order, "statuses": OrderStatus, "transitions": ALLOWED_TRANSITIONS},
    )
