from __future__ import annotations
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.client import Client


class OrderStatus(str, Enum):
    CREATED = "créée"
    CONFIRMED = "confirmée"
    SHIPPED = "expédiée"
    DELIVERED = "livrée"
    CANCELED = "annulée"


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reference: str
    total_amount: float
    status: OrderStatus = Field(default=OrderStatus.CREATED)

    client_id: int = Field(foreign_key="client.id")
    client: Optional[Client] = Relationship(back_populates="orders")