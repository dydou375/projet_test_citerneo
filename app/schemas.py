from pydantic import BaseModel, EmailStr, field_validator

from app.models.commande import OrderStatus


class ClientCreate(BaseModel):
    name: str
    email: EmailStr        # Pydantic vérifie le format email automatiquement
    phone: str
    address: str

    @field_validator("name", "phone", "address")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()


class OrderCreate(BaseModel):
    reference: str
    total_amount: float
    client_id: int

    @field_validator("total_amount")
    @classmethod
    def positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant doit être positif")
        return v

    @field_validator("reference")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La référence ne peut pas être vide")
        return v.strip()


class OrderStatusUpdate(BaseModel):
    status: OrderStatus    # Pydantic rejette automatiquement toute valeur hors de l'enum
