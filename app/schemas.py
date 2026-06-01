import re

from pydantic import BaseModel, EmailStr, field_validator

from app.models.commande import OrderStatus

# Accepte : 0612345678 | +33612345678 | 0033612345678 (espaces et tirets tolérés)
PHONE_RE = re.compile(r"^(?:\+33|0033|0)[1-9](?:[\s.\-]?\d{2}){4}$")

# Doit commencer par un numéro de rue (ex: "12 rue de la Paix")
ADDRESS_RE = re.compile(r"^\d+.+")


class ClientCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()

    @field_validator("phone")
    @classmethod
    def phone_valid(cls, v: str) -> str:
        cleaned = v.strip()
        if not PHONE_RE.match(cleaned):
            raise ValueError("Numéro invalide (ex : 0612345678 ou +33612345678)")
        return cleaned

    @field_validator("address")
    @classmethod
    def address_valid(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 5:
            raise ValueError("Adresse trop courte")
        if not ADDRESS_RE.match(cleaned):
            raise ValueError("L'adresse doit commencer par un numéro de rue (ex : 12 rue de la Paix)")
        return cleaned


class OrderCreate(BaseModel):
    reference: str
    total_amount: float
    client_id: int

    @field_validator("total_amount")# On vérifie que le montant total est positif
    @classmethod
    def positive_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant doit être positif")
        return v

    @field_validator("reference")# On vérifie que la référence n'est pas vide ou composée uniquement d'espaces
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La référence ne peut pas être vide")
        return v.strip()


class OrderStatusUpdate(BaseModel):
    status: OrderStatus    # Pydantic rejette automatiquement toute valeur hors de l'enum
