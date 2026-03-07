from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import Contact
from app.models.reminder import (
    Reminder,
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=ReminderListResponse)
async def list_reminders(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    upcoming_days: Optional[int] = Query(None, description="Filter reminders within X days"),
    current_user: User = Depends(get_current_user),
):
    """List all reminders for the current user."""
    try:
        query_conditions = [Reminder.user_id == current_user.user_id]

        if completed is not None:
            query_conditions.append(Reminder.completed == completed)

        if upcoming_days is not None:
            from datetime import timedelta
            future_date = datetime.utcnow() + timedelta(days=upcoming_days)
            query_conditions.append(Reminder.reminder_date <= future_date)
            query_conditions.append(Reminder.reminder_date >= datetime.utcnow())

        reminders = await Reminder.find(*query_conditions).sort(Reminder.reminder_date).to_list()

        # Get contact names
        contact_ids = list(set(r.contact_id for r in reminders))
        contacts = await Contact.find({"contact_id": {"$in": contact_ids}}).to_list()
        contact_names = {c.contact_id: c.name for c in contacts}

        reminder_responses = [
            ReminderResponse.from_reminder(reminder, contact_names.get(reminder.contact_id))
            for reminder in reminders
        ]

        # Count pending and overdue
        now = datetime.utcnow()
        pending_count = sum(1 for r in reminders if not r.completed)
        overdue_count = sum(1 for r in reminders if not r.completed and r.reminder_date < now)

        return ReminderListResponse(
            reminders=reminder_responses,
            total=len(reminder_responses),
            pending_count=pending_count,
            overdue_count=overdue_count,
        )

    except Exception as e:
        logger.error(f"Error listing reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener los recordatorios"
        )


@router.post("", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new reminder."""
    # Verify contact exists and belongs to user
    contact = await Contact.find_one(
        Contact.contact_id == reminder_data.contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    try:
        reminder = Reminder(
            contact_id=reminder_data.contact_id,
            user_id=current_user.user_id,
            reminder_date=reminder_data.reminder_date,
            reason=reminder_data.reason,
            is_birthday=reminder_data.is_birthday,
        )
        await reminder.insert()

        logger.info(f"Reminder created for contact: {contact.name}")

        return ReminderResponse.from_reminder(reminder, contact.name)

    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el recordatorio"
        )


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get a specific reminder by ID."""
    reminder = await Reminder.find_one(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == current_user.user_id,
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recordatorio no encontrado"
        )

    contact = await Contact.find_one(Contact.contact_id == reminder.contact_id)
    contact_name = contact.name if contact else None

    return ReminderResponse.from_reminder(reminder, contact_name)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    reminder_data: ReminderUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a reminder."""
    reminder = await Reminder.find_one(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == current_user.user_id,
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recordatorio no encontrado"
        )

    try:
        update_data = reminder_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(reminder, field, value)

        reminder.updated_at = datetime.utcnow()
        await reminder.save()

        contact = await Contact.find_one(Contact.contact_id == reminder.contact_id)
        contact_name = contact.name if contact else None

        logger.info(f"Reminder updated: {reminder.reminder_id}")

        return ReminderResponse.from_reminder(reminder, contact_name)

    except Exception as e:
        logger.error(f"Error updating reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar el recordatorio"
        )


@router.patch("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
):
    """Mark a reminder as completed."""
    reminder = await Reminder.find_one(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == current_user.user_id,
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recordatorio no encontrado"
        )

    try:
        reminder.completed = True
        reminder.completed_at = datetime.utcnow()
        reminder.updated_at = datetime.utcnow()
        await reminder.save()

        contact = await Contact.find_one(Contact.contact_id == reminder.contact_id)
        contact_name = contact.name if contact else None

        logger.info(f"Reminder completed: {reminder.reminder_id}")

        return ReminderResponse.from_reminder(reminder, contact_name)

    except Exception as e:
        logger.error(f"Error completing reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al completar el recordatorio"
        )


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a reminder."""
    reminder = await Reminder.find_one(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == current_user.user_id,
    )

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recordatorio no encontrado"
        )

    try:
        await reminder.delete()
        logger.info(f"Reminder deleted: {reminder_id}")

    except Exception as e:
        logger.error(f"Error deleting reminder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el recordatorio"
        )
