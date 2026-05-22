from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from typing import List, Optional



class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    address: str
    created_at: datetime = Field(default_factory=datetime.now)

    orders: List["commande"] = Relationship(back_populates="client")

