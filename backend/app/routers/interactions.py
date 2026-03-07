from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import Contact
from app.models.interaction import (
    Interaction,
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=InteractionListResponse)
async def list_interactions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    contact_id: Optional[str] = Query(None),
    is_highlight: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List all interactions for the current user (timeline)."""
    try:
        # Build query
        query_conditions = [Interaction.user_id == current_user.user_id]

        if contact_id:
            query_conditions.append(Interaction.contact_id == contact_id)

        if is_highlight is not None:
            query_conditions.append(Interaction.is_highlight == is_highlight)

        # Count total
        total = await Interaction.find(*query_conditions).count()

        # Get interactions with pagination
        interactions = await Interaction.find(
            *query_conditions
        ).sort(-Interaction.date).skip(offset).limit(limit).to_list()

        # Get contact names for each interaction
        contact_ids = list(set(i.contact_id for i in interactions))
        contacts = await Contact.find(
            {"contact_id": {"$in": contact_ids}}
        ).to_list()
        contact_names = {c.contact_id: c.name for c in contacts}

        interaction_responses = [
            InteractionResponse.from_interaction(
                interaction,
                contact_names.get(interaction.contact_id)
            )
            for interaction in interactions
        ]

        return InteractionListResponse(
            interactions=interaction_responses,
            total=total,
        )

    except Exception as e:
        logger.error(f"Error listing interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener las interacciones"
        )


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
async def create_interaction(
    interaction_data: InteractionCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new interaction."""
    # Verify contact exists and belongs to user
    contact = await Contact.find_one(
        Contact.contact_id == interaction_data.contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    try:
        interaction = Interaction(
            contact_id=interaction_data.contact_id,
            user_id=current_user.user_id,
            date=interaction_data.date or datetime.utcnow(),
            quick_summary=interaction_data.quick_summary,
            emotion=interaction_data.emotion,
            topics=interaction_data.topics,
            is_highlight=interaction_data.is_highlight,
        )
        await interaction.insert()

        # Update contact's last interaction
        contact.last_interaction_date = interaction.date
        contact.last_interaction_summary = interaction.quick_summary
        contact.updated_at = datetime.utcnow()
        await contact.save()

        logger.info(f"Interaction created for contact: {contact.name}")

        return InteractionResponse.from_interaction(interaction, contact.name)

    except Exception as e:
        logger.error(f"Error creating interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear la interacción"
        )


@router.get("/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific interaction by ID."""
    interaction = await Interaction.find_one(
        Interaction.interaction_id == interaction_id,
        Interaction.user_id == current_user.user_id,
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interacción no encontrada"
        )

    # Get contact name
    contact = await Contact.find_one(Contact.contact_id == interaction.contact_id)
    contact_name = contact.name if contact else None

    return InteractionResponse.from_interaction(interaction, contact_name)


@router.put("/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: str,
    interaction_data: InteractionUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update an interaction."""
    interaction = await Interaction.find_one(
        Interaction.interaction_id == interaction_id,
        Interaction.user_id == current_user.user_id,
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interacción no encontrada"
        )

    try:
        # Update only provided fields
        update_data = interaction_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(interaction, field, value)

        interaction.updated_at = datetime.utcnow()
        await interaction.save()

        # If summary was updated, update contact's last summary too
        if interaction_data.quick_summary:
            contact = await Contact.find_one(Contact.contact_id == interaction.contact_id)
            if contact:
                # Check if this is the most recent interaction
                latest = await Interaction.find(
                    Interaction.contact_id == interaction.contact_id
                ).sort(-Interaction.date).first_or_none()

                if latest and latest.interaction_id == interaction.interaction_id:
                    contact.last_interaction_summary = interaction.quick_summary
                    await contact.save()

        # Get contact name
        contact = await Contact.find_one(Contact.contact_id == interaction.contact_id)
        contact_name = contact.name if contact else None

        logger.info(f"Interaction updated: {interaction.interaction_id}")

        return InteractionResponse.from_interaction(interaction, contact_name)

    except Exception as e:
        logger.error(f"Error updating interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la interacción"
        )


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interaction(
    interaction_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete an interaction."""
    interaction = await Interaction.find_one(
        Interaction.interaction_id == interaction_id,
        Interaction.user_id == current_user.user_id,
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interacción no encontrada"
        )

    try:
        contact_id = interaction.contact_id
        await interaction.delete()

        # Update contact's last interaction to the previous one
        contact = await Contact.find_one(Contact.contact_id == contact_id)
        if contact:
            latest = await Interaction.find(
                Interaction.contact_id == contact_id
            ).sort(-Interaction.date).first_or_none()

            if latest:
                contact.last_interaction_date = latest.date
                contact.last_interaction_summary = latest.quick_summary
            else:
                contact.last_interaction_date = None
                contact.last_interaction_summary = None

            await contact.save()

        logger.info(f"Interaction deleted: {interaction_id}")

    except Exception as e:
        logger.error(f"Error deleting interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la interacción"
        )
