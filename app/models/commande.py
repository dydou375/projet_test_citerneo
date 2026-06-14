from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


# str, Enum → les valeurs sont de vraies chaînes Python, SQLite stocke "créée" pas "CREATED"
class OrderStatus(str, Enum):
    CREATED = "créée"
    CONFIRMED = "confirmée"
    SHIPPED = "expédiée"
    DELIVERED = "livrée"
    CANCELED = "annulée"


# liste vide = état terminal, aucune transition possible depuis cet état
ALLOWED_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.CREATED:   [OrderStatus.CONFIRMED, OrderStatus.CANCELED],
    OrderStatus.CONFIRMED: [OrderStatus.SHIPPED,   OrderStatus.CANCELED],
    OrderStatus.SHIPPED:   [OrderStatus.DELIVERED, OrderStatus.CANCELED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELED:  [],
}


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str
    created_at: datetime = Field(default_factory=datetime.now)
    total_amount: float
    status: OrderStatus = Field(default=OrderStatus.CREATED)

    # ondelete="CASCADE" → si le client est supprimé, ses commandes le sont aussi côté base
    client_id: int = Field(foreign_key="client.id", ondelete="CASCADE")
    client: Optional["Client"] = Relationship(back_populates="orders")
