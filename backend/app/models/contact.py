from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import uuid4


class Contact(Document):
    """Contact document model."""
    contact_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    user_id: Indexed(str)

    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None

    relationship_type: str = Field(
        default="amigo",
        description="Type of relationship: familia, amigo, pareja, trabajo, conocido"
    )

    birthday: Optional[date] = None

    last_interaction_date: Optional[datetime] = None
    last_interaction_summary: Optional[str] = None

    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "contacts"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Carlos López",
                "phone": "+34612345678",
                "email": "carlos@email.com",
                "relationship_type": "amigo",
                "birthday": "1990-05-15",
            }
        }


class ContactCreate(BaseModel):
    """Schema for creating a new contact."""
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    relationship_type: str = "amigo"
    birthday: Optional[date] = None
    notes: Optional[str] = None


class ContactUpdate(BaseModel):
    """Schema for updating a contact."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    relationship_type: Optional[str] = None
    birthday: Optional[date] = None
    notes: Optional[str] = None


class ContactResponse(BaseModel):
    """Schema for contact response."""
    contact_id: str
    user_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    photo_url: Optional[str]
    relationship_type: str
    birthday: Optional[date]
    last_interaction_date: Optional[datetime]
    last_interaction_summary: Optional[str]
    notes: Optional[str]
    days_since_last_interaction: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_contact(cls, contact: Contact) -> "ContactResponse":
        """Create response from Contact document with computed fields."""
        days_since = None
        if contact.last_interaction_date:
            delta = datetime.utcnow() - contact.last_interaction_date
            days_since = delta.days

        return cls(
            contact_id=contact.contact_id,
            user_id=contact.user_id,
            name=contact.name,
            phone=contact.phone,
            email=contact.email,
            photo_url=contact.photo_url,
            relationship_type=contact.relationship_type,
            birthday=contact.birthday,
            last_interaction_date=contact.last_interaction_date,
            last_interaction_summary=contact.last_interaction_summary,
            notes=contact.notes,
            days_since_last_interaction=days_since,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
        )


class ContactListResponse(BaseModel):
    """Schema for list of contacts response."""
    contacts: List[ContactResponse]
    total: int
