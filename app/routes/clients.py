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


@router.get("/", response_class=HTMLResponse) # Cet endpoint affiche la liste de tous les clients. On récupère tous les clients de la base de données et on les passe au template pour les afficher.
def list_clients(request: Request, session: Session = Depends(get_session)):
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(request, "clients/index.html", {"clients": clients})


@router.post("/", response_class=HTMLResponse) # Cet endpoint permet de créer un nouveau client. Les données sont envoyées via un formulaire, et on utilise Pydantic pour valider ces données avant de les insérer dans la base de données.
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
    clients = session.exec(select(Client)).all()
    return templates.TemplateResponse(request, "clients/_list.html", {"clients": clients})


@router.get("/{client_id}/commandes", response_class=HTMLResponse) #    Cet endpoint affiche la liste des commandes d'un client spécifique. On vérifie d'abord que le client existe, puis on récupère toutes les commandes associées à ce client pour les afficher dans le template.
def get_client_orders(client_id: int, request: Request, session: Session = Depends(get_session)):
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    orders = session.exec(select(Order).where(Order.client_id == client_id)).all()
    return templates.TemplateResponse(request, "clients/commandes.html", {"client": client, "orders": orders})
