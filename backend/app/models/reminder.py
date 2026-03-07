from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import uuid4


class Reminder(Document):
    """Reminder document model."""
    reminder_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    contact_id: Indexed(str)
    user_id: Indexed(str)

    reminder_date: datetime
    reason: str = Field(..., min_length=1, max_length=500)

    is_birthday: bool = Field(default=False)
    completed: bool = Field(default=False)
    completed_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "reminders"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "contact_id": "uuid-here",
                "reminder_date": "2024-03-15T10:00:00",
                "reason": "Preguntarle cómo fue su entrevista de trabajo",
                "is_birthday": False,
            }
        }


class ReminderCreate(BaseModel):
    """Schema for creating a new reminder."""
    contact_id: str
    reminder_date: datetime
    reason: str = Field(..., min_length=1, max_length=500)
    is_birthday: bool = False


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""
    reminder_date: Optional[datetime] = None
    reason: Optional[str] = Field(None, min_length=1, max_length=500)
    is_birthday: Optional[bool] = None


class ReminderResponse(BaseModel):
    """Schema for reminder response."""
    reminder_id: str
    contact_id: str
    user_id: str
    contact_name: Optional[str] = None
    reminder_date: datetime
    reason: str
    is_birthday: bool
    completed: bool
    completed_at: Optional[datetime]
    is_overdue: bool = False
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_reminder(
        cls,
        reminder: Reminder,
        contact_name: Optional[str] = None
    ) -> "ReminderResponse":
        """Create response from Reminder document."""
        is_overdue = (
            not reminder.completed
            and reminder.reminder_date < datetime.utcnow()
        )

        return cls(
            reminder_id=reminder.reminder_id,
            contact_id=reminder.contact_id,
            user_id=reminder.user_id,
            contact_name=contact_name,
            reminder_date=reminder.reminder_date,
            reason=reminder.reason,
            is_birthday=reminder.is_birthday,
            completed=reminder.completed,
            completed_at=reminder.completed_at,
            is_overdue=is_overdue,
            created_at=reminder.created_at,
            updated_at=reminder.updated_at,
        )


class ReminderListResponse(BaseModel):
    """Schema for list of reminders response."""
    reminders: List[ReminderResponse]
    total: int
    pending_count: int
    overdue_count: int
