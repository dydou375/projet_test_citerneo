from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    address: str
    created_at: datetime = Field(default_factory=datetime.now)

    orders: List["Order"] = Relationship(back_populates="client")
