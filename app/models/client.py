from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# table=True indique à SQLModel que cette classe correspond à une vraie table SQL.
class Client(SQLModel, table=True):
    # Optional[int] car l'id est None avant insertion ; SQLite le génère automatiquement.
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    address: str

    # default_factory=datetime.now : appelle la fonction à chaque création d'objet.
    # Si on avait mis default=datetime.now(), la date serait figée au démarrage de l'app.
    created_at: datetime = Field(default_factory=datetime.now)

    # Ce champ n'existe pas en base : c'est une relation virtuelle côté Python.
    # Il permet d'accéder aux commandes d'un client : client.orders
    # "Order" en chaîne évite un import circulaire (Order est défini dans un autre fichier).
    orders: List["Order"] = Relationship(back_populates="client")
