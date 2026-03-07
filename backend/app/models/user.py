from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4


class UserSettings(BaseModel):
    """User preferences and settings."""
    gender_preference: str = Field(
        default="neutro",
        description="Gender preference for language: masculino, femenino, neutro, no_especificado"
    )
    coaching_level: str = Field(
        default="moderado",
        description="Coaching intensity: activo, moderado, sutil"
    )
    ritual_time: str = Field(
        default="09:00",
        description="Preferred time for daily ritual notification"
    )
    neglect_days: int = Field(
        default=14,
        description="Days without contact before marking as neglected"
    )
    notifications_enabled: bool = Field(
        default=True,
        description="Whether push notifications are enabled"
    )


class BondyConfig(BaseModel):
    """Configuration for Bondy AI assistant."""
    name: str = Field(
        default="Bondy",
        description="Custom name for the AI assistant"
    )
    coaching_level: str = Field(
        default="moderado",
        description="How proactive Bondy should be"
    )
    gender: str = Field(
        default="femenino",
        description="Bondy's gender for language purposes"
    )
    welcome_messages_enabled: bool = Field(
        default=True,
        description="Show welcome messages"
    )
    birthday_reminders_enabled: bool = Field(
        default=True,
        description="Remind about contact birthdays"
    )


class User(Document):
    """User document model."""
    user_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    email: Indexed(EmailStr, unique=True)
    name: str
    picture: Optional[str] = None
    auth_provider: str = Field(default="google")

    settings: UserSettings = Field(default_factory=UserSettings)
    bondy_config: BondyConfig = Field(default_factory=BondyConfig)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@email.com",
                "name": "María García",
                "picture": "https://example.com/photo.jpg",
                "auth_provider": "google",
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    name: str
    picture: Optional[str] = None
    auth_provider: str = "google"


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    picture: Optional[str] = None
    settings: Optional[UserSettings] = None
    bondy_config: Optional[BondyConfig] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    user_id: str
    email: str
    name: str
    picture: Optional[str]
    auth_provider: str
    settings: UserSettings
    bondy_config: BondyConfig
    created_at: datetime
