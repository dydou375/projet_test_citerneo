from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlmodel import Session, select

from app.config import templates
from app.database import engine
from app.models import Client, Order
from app.schemas import ClientCreate

router = APIRouter(prefix="/clients", tags=["Clients"])


def get_session():
    with Session(engine) as session:
        yield session


@router.get("/", response_class=HTMLResponse)
def list_clients(request: Request, session: Session = Depends(get_session)):
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse("clients/index.html", {"request": request, "clients": clients})


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
    return templates.TemplateResponse("clients/_list.html", {"request": request, "clients": clients})


@router.get("/{client_id}/commandes", response_class=HTMLResponse)
def get_client_orders(client_id: int, request: Request, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    orders = session.exec(select(Order).where(Order.client_id == client_id)).all()
    return templates.TemplateResponse(
        "clients/commandes.html",
        {"request": request, "client": client, "orders": orders},
    )
