from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
import logging
import random

from app.core.security import get_current_user
from app.models.user import User
from app.models.contact import Contact, ContactResponse
from app.models.interaction import Interaction
from app.models.ritual_streak import RitualStreak, RitualStreakResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class PersonOfDayResponse(BaseModel):
    """Response for person of the day."""
    contact: ContactResponse
    context: str
    reason: str
    days_since_contact: Optional[int]
    suggested_actions: List[str]


class RitualStatsResponse(BaseModel):
    """Response for ritual statistics."""
    streak: RitualStreakResponse
    total_contacts: int
    neglected_contacts: int
    interactions_this_week: int
    interactions_this_month: int
    upcoming_birthdays: List[dict]


class InsightsResponse(BaseModel):
    """Response for AI-generated insights."""
    insights: List[str]
    generated_at: datetime


async def get_person_of_day_algorithm(user: User) -> Optional[Contact]:
    """
    Algorithm to select the person of the day.

    Priority:
    1. Contacts with upcoming birthdays (within 7 days)
    2. Contacts with pending reminders
    3. Most neglected contacts (longest since last interaction)
    4. Contacts never interacted with
    5. Random from remaining
    """
    neglect_days = user.settings.neglect_days

    # Get all user's contacts
    contacts = await Contact.find(Contact.user_id == user.user_id).to_list()

    if not contacts:
        return None

    today = date.today()

    # 1. Check for upcoming birthdays (within 7 days)
    birthday_contacts = []
    for contact in contacts:
        if contact.birthday:
            # Create this year's birthday
            this_year_birthday = contact.birthday.replace(year=today.year)
            if this_year_birthday < today:
                this_year_birthday = this_year_birthday.replace(year=today.year + 1)

            days_until = (this_year_birthday - today).days
            if 0 <= days_until <= 7:
                birthday_contacts.append((contact, days_until))

    if birthday_contacts:
        # Sort by closest birthday
        birthday_contacts.sort(key=lambda x: x[1])
        return birthday_contacts[0][0]

    # 2. Check for pending reminders
    from app.models.reminder import Reminder
    pending_reminders = await Reminder.find(
        Reminder.user_id == user.user_id,
        Reminder.completed == False,
        Reminder.reminder_date <= datetime.utcnow() + timedelta(days=1),
    ).to_list()

    if pending_reminders:
        # Get the contact for the most urgent reminder
        reminder = pending_reminders[0]
        for contact in contacts:
            if contact.contact_id == reminder.contact_id:
                return contact

    # 3. Most neglected contacts
    neglected = []
    now = datetime.utcnow()

    for contact in contacts:
        if contact.last_interaction_date:
            days_since = (now - contact.last_interaction_date).days
            if days_since >= neglect_days:
                neglected.append((contact, days_since))
        else:
            # Never interacted - high priority
            neglected.append((contact, 999))

    if neglected:
        # Sort by most neglected
        neglected.sort(key=lambda x: x[1], reverse=True)
        # Pick from top 3 with some randomness
        top_neglected = neglected[:3]
        return random.choice(top_neglected)[0]

    # 4. Random contact
    return random.choice(contacts)


async def generate_context(contact: Contact, user: User) -> str:
    """
    Generate context for reconnecting with contact.
    Uses Gemini AI if available, otherwise returns default message.
    """
    from app.core.config import settings

    days_since = None
    if contact.last_interaction_date:
        days_since = (datetime.utcnow() - contact.last_interaction_date).days

    # Try to use Gemini if configured
    if settings.gemini_api_key:
        try:
            from app.services.gemini import generate_person_context
            context = await generate_person_context(contact, user)
            if context:
                return context
        except Exception as e:
            logger.warning(f"Gemini API error, using fallback: {e}")

    # Fallback context
    relationship_labels = {
        "familia": "tu familia",
        "amigo": "tu amistad",
        "pareja": "tu relación",
        "trabajo": "tu conexión profesional",
        "conocido": "este conocido",
    }

    rel_label = relationship_labels.get(contact.relationship_type, "esta persona")

    if days_since is None:
        return f"Todavía no has registrado ninguna interacción con {contact.name}. Es un buen momento para fortalecer {rel_label}."
    elif days_since > 30:
        return f"Han pasado más de un mes desde tu última conversación con {contact.name}. Seguro que le alegrará saber de ti."
    elif days_since > 14:
        return f"Hace {days_since} días que no contactas con {contact.name}. Un mensaje breve puede mantener viva {rel_label}."
    else:
        if contact.last_interaction_summary:
            return f"La última vez hablasteis de: {contact.last_interaction_summary}. Podrías preguntarle cómo va todo."
        return f"Hace poco que hablaste con {contact.name}. Mantén el momentum de {rel_label}."


@router.get("/person-of-day", response_model=PersonOfDayResponse)
async def get_person_of_day(
    current_user: User = Depends(get_current_user),
):
    """Get the suggested person to contact today."""
    contact = await get_person_of_day_algorithm(current_user)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes contactos registrados. Añade algunos para empezar."
        )

    # Calculate days since last contact
    days_since = None
    if contact.last_interaction_date:
        days_since = (datetime.utcnow() - contact.last_interaction_date).days

    # Generate context
    context = await generate_context(contact, current_user)

    # Determine reason
    today = date.today()
    reason = "Contacto sugerido"

    if contact.birthday:
        this_year_birthday = contact.birthday.replace(year=today.year)
        if this_year_birthday < today:
            this_year_birthday = this_year_birthday.replace(year=today.year + 1)
        days_until = (this_year_birthday - today).days
        if days_until == 0:
            reason = "¡Es su cumpleaños hoy!"
        elif days_until <= 7:
            reason = f"Cumpleaños en {days_until} días"
    elif days_since is None:
        reason = "Primera interacción pendiente"
    elif days_since > current_user.settings.neglect_days:
        reason = f"Sin contacto hace {days_since} días"

    # Suggested actions
    suggested_actions = [
        "Enviar un mensaje",
        "Hacer una llamada",
        "Planear una quedada",
    ]

    return PersonOfDayResponse(
        contact=ContactResponse.from_contact(contact),
        context=context,
        reason=reason,
        days_since_contact=days_since,
        suggested_actions=suggested_actions,
    )


@router.get("/stats", response_model=RitualStatsResponse)
async def get_ritual_stats(
    current_user: User = Depends(get_current_user),
):
    """Get statistics for the ritual dashboard."""
    # Get or create streak
    streak = await RitualStreak.find_one(RitualStreak.user_id == current_user.user_id)
    if not streak:
        streak = RitualStreak(user_id=current_user.user_id)
        await streak.insert()

    # Count contacts
    total_contacts = await Contact.find(Contact.user_id == current_user.user_id).count()

    # Count neglected contacts
    neglect_days = current_user.settings.neglect_days
    neglect_threshold = datetime.utcnow() - timedelta(days=neglect_days)

    neglected_contacts = await Contact.find(
        Contact.user_id == current_user.user_id,
        {"$or": [
            {"last_interaction_date": {"$lt": neglect_threshold}},
            {"last_interaction_date": None},
        ]}
    ).count()

    # Count interactions this week and month
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)

    interactions_week = await Interaction.find(
        Interaction.user_id == current_user.user_id,
        Interaction.date >= week_ago,
    ).count()

    interactions_month = await Interaction.find(
        Interaction.user_id == current_user.user_id,
        Interaction.date >= month_ago,
    ).count()

    # Get upcoming birthdays (next 30 days)
    today = date.today()
    contacts = await Contact.find(
        Contact.user_id == current_user.user_id,
        Contact.birthday != None,
    ).to_list()

    upcoming_birthdays = []
    for contact in contacts:
        if contact.birthday:
            this_year_birthday = contact.birthday.replace(year=today.year)
            if this_year_birthday < today:
                this_year_birthday = this_year_birthday.replace(year=today.year + 1)

            days_until = (this_year_birthday - today).days
            if 0 <= days_until <= 30:
                upcoming_birthdays.append({
                    "contact_id": contact.contact_id,
                    "name": contact.name,
                    "birthday": contact.birthday.isoformat(),
                    "days_until": days_until,
                })

    upcoming_birthdays.sort(key=lambda x: x["days_until"])

    return RitualStatsResponse(
        streak=RitualStreakResponse.from_streak(streak),
        total_contacts=total_contacts,
        neglected_contacts=neglected_contacts,
        interactions_this_week=interactions_week,
        interactions_this_month=interactions_month,
        upcoming_birthdays=upcoming_birthdays[:5],  # Limit to 5
    )


@router.post("/complete", response_model=RitualStreakResponse)
async def complete_ritual(
    current_user: User = Depends(get_current_user),
):
    """Mark today's ritual as completed and update streak."""
    streak = await RitualStreak.find_one(RitualStreak.user_id == current_user.user_id)

    if not streak:
        streak = RitualStreak(user_id=current_user.user_id)

    completed = streak.complete_ritual()

    if completed:
        await streak.save()
        logger.info(f"Ritual completed for user {current_user.user_id}, streak: {streak.current_streak}")

    return RitualStreakResponse.from_streak(streak)


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    current_user: User = Depends(get_current_user),
):
    """Get AI-generated insights about relationships."""
    from app.core.config import settings

    # Gather data for insights
    total_contacts = await Contact.find(Contact.user_id == current_user.user_id).count()

    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_interactions = await Interaction.find(
        Interaction.user_id == current_user.user_id,
        Interaction.date >= week_ago,
    ).count()

    neglect_threshold = datetime.utcnow() - timedelta(days=current_user.settings.neglect_days)
    neglected_count = await Contact.find(
        Contact.user_id == current_user.user_id,
        {"$or": [
            {"last_interaction_date": {"$lt": neglect_threshold}},
            {"last_interaction_date": None},
        ]}
    ).count()

    # Try Gemini if available
    if settings.gemini_api_key:
        try:
            from app.services.gemini import generate_insights
            insights = await generate_insights(
                total_contacts=total_contacts,
                recent_interactions=recent_interactions,
                neglected_count=neglected_count,
                user=current_user,
            )
            if insights:
                return InsightsResponse(
                    insights=insights,
                    generated_at=datetime.utcnow(),
                )
        except Exception as e:
            logger.warning(f"Gemini API error, using fallback: {e}")

    # Fallback insights
    insights = []

    if total_contacts == 0:
        insights.append("Empieza añadiendo tus contactos más importantes. Te ayudaré a mantener esas relaciones vivas.")
    else:
        if neglected_count > 0:
            pct = round((neglected_count / total_contacts) * 100)
            insights.append(f"Tienes {neglected_count} contactos ({pct}%) que no has contactado en más de {current_user.settings.neglect_days} días. Un mensaje corto puede hacer mucho.")

        if recent_interactions > 0:
            insights.append(f"¡Gran semana! Has tenido {recent_interactions} interacciones. Sigue así para mantener tus relaciones fuertes.")
        else:
            insights.append("Esta semana no has registrado interacciones. Intenta conectar con al menos una persona hoy.")

        if neglected_count == 0 and total_contacts > 0:
            insights.append("¡Excelente! Estás al día con todos tus contactos. Sigue manteniendo ese equilibrio.")

    return InsightsResponse(
        insights=insights,
        generated_at=datetime.utcnow(),
    )
