from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Client(SQLModel, table=True):
    # None avant insertion — SQLite génère l'id automatiquement au commit
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    address: str

    # default_factory=datetime.now : appelle la fonction à chaque création d'objet.
    # Si on avait mis default=datetime.now(), la date serait figée au démarrage de l'app.
    created_at: datetime = Field(default_factory=datetime.now)

    # champ virtuel (pas en base) — permet d'écrire client.orders en Python
    # "Order" en chaîne de caractères pour éviter l'import circulaire
    orders: List["Order"] = Relationship(back_populates="client")
