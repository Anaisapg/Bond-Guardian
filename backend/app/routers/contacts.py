from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import (
    Contact,
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort_by: str = Query("name", description="Sort by: name, last_interaction, created_at"),
    order: str = Query("asc", description="Sort order: asc, desc"),
    current_user: User = Depends(get_current_user),
):
    """List all contacts for the current user."""
    try:
        # Build query
        query = Contact.find(Contact.user_id == current_user.user_id)

        # Apply filters
        if relationship_type:
            query = query.find(Contact.relationship_type == relationship_type)

        if search:
            # Case-insensitive search
            query = query.find({"name": {"$regex": search, "$options": "i"}})

        # Get all matching contacts
        contacts = await query.to_list()

        # Sort in Python (Beanie sorting can be complex)
        if sort_by == "name":
            contacts.sort(key=lambda c: c.name.lower(), reverse=(order == "desc"))
        elif sort_by == "last_interaction":
            contacts.sort(
                key=lambda c: c.last_interaction_date or datetime.min,
                reverse=(order == "desc")
            )
        elif sort_by == "created_at":
            contacts.sort(key=lambda c: c.created_at, reverse=(order == "desc"))

        # Convert to response format
        contact_responses = [
            ContactResponse.from_contact(contact) for contact in contacts
        ]

        return ContactListResponse(
            contacts=contact_responses,
            total=len(contact_responses),
        )

    except Exception as e:
        logger.error(f"Error listing contacts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los contactos"
        )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new contact."""
    try:
        contact = Contact(
            user_id=current_user.user_id,
            name=contact_data.name,
            phone=contact_data.phone,
            email=contact_data.email,
            photo_url=contact_data.photo_url,
            relationship_type=contact_data.relationship_type,
            birthday=contact_data.birthday,
            notes=contact_data.notes,
        )
        await contact.insert()

        logger.info(f"Contact created: {contact.name} for user {current_user.user_id}")

        return ContactResponse.from_contact(contact)

    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el contacto"
        )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific contact by ID."""
    contact = await Contact.find_one(
        Contact.contact_id == contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    return ContactResponse.from_contact(contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a contact."""
    contact = await Contact.find_one(
        Contact.contact_id == contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    try:
        # Update only provided fields
        update_data = contact_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(contact, field, value)

        contact.updated_at = datetime.utcnow()
        await contact.save()

        logger.info(f"Contact updated: {contact.name}")

        return ContactResponse.from_contact(contact)

    except Exception as e:
        logger.error(f"Error updating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el contacto"
        )


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a contact."""
    contact = await Contact.find_one(
        Contact.contact_id == contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    try:
        # Also delete related interactions and reminders
        from app.models.interaction import Interaction
        from app.models.reminder import Reminder

        await Interaction.find(Interaction.contact_id == contact_id).delete()
        await Reminder.find(Reminder.contact_id == contact_id).delete()

        await contact.delete()

        logger.info(f"Contact deleted: {contact.name}")

    except Exception as e:
        logger.error(f"Error deleting contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el contacto"
        )


@router.get("/{contact_id}/interactions")
async def get_contact_interactions(
    contact_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get all interactions for a specific contact."""
    # Verify contact exists and belongs to user
    contact = await Contact.find_one(
        Contact.contact_id == contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    from app.models.interaction import Interaction, InteractionResponse, InteractionListResponse

    try:
        # Get interactions for this contact
        total = await Interaction.find(Interaction.contact_id == contact_id).count()

        interactions = await Interaction.find(
            Interaction.contact_id == contact_id
        ).sort(-Interaction.date).skip(offset).limit(limit).to_list()

        interaction_responses = [
            InteractionResponse.from_interaction(interaction, contact.name)
            for interaction in interactions
        ]

        return InteractionListResponse(
            interactions=interaction_responses,
            total=total,
        )

    except Exception as e:
        logger.error(f"Error getting contact interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las interacciones"
        )
