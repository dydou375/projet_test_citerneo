from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlmodel import Session, select

from app.auth import require_auth
from app.config import templates
from app.database import get_session
from app.models import Client, Order
from app.schemas import ClientCreate

# toutes les routes de ce fichier sont protégées d'un coup, pas besoin de le répéter sur chaque fonction
router = APIRouter(prefix="/clients", tags=["Clients"], dependencies=[Depends(require_auth)])


@router.get("/", response_class=HTMLResponse)
def list_clients(request: Request, session: Session = Depends(get_session)):
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(request, "clients/index.html", {"clients": clients})


@router.post("/", response_class=HTMLResponse)
def create_client(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        data = ClientCreate(name=name, email=email, phone=phone, address=address)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    client = Client(**data.model_dump())
    session.add(client)
    session.commit()

    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(request, "clients/_list.html", {"clients": clients})


@router.delete("/{client_id}", response_class=HTMLResponse)
def delete_client(client_id: int, request: Request, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    session.delete(client)
    session.commit()
    # les commandes liées sont supprimées automatiquement par SQLite (CASCADE défini dans le modèle)
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(request, "clients/_list.html", {"clients": clients})


@router.get("/{client_id}/commandes", response_class=HTMLResponse)
def get_client_orders(client_id: int, request: Request, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    orders = session.exec(select(Order).where(Order.client_id == client_id)).all()
    return templates.TemplateResponse(request, "clients/commandes.html", {"client": client, "orders": orders})
