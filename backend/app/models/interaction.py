from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import uuid4
from enum import Enum


class EmotionType(str, Enum):
    """Emotion types for interactions."""
    MUY_POSITIVO = "muy_positivo"
    POSITIVO = "positivo"
    NEUTRAL = "neutral"
    NEGATIVO = "negativo"
    MUY_NEGATIVO = "muy_negativo"


EMOTION_EMOJIS = {
    EmotionType.MUY_POSITIVO: "😄",
    EmotionType.POSITIVO: "🙂",
    EmotionType.NEUTRAL: "😐",
    EmotionType.NEGATIVO: "😔",
    EmotionType.MUY_NEGATIVO: "😢",
}


class Interaction(Document):
    """Interaction document model."""
    interaction_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    contact_id: Indexed(str)
    user_id: Indexed(str)

    date: datetime = Field(default_factory=datetime.utcnow)
    quick_summary: str = Field(..., min_length=1, max_length=500)

    emotion: EmotionType = Field(default=EmotionType.POSITIVO)
    topics: List[str] = Field(default_factory=list)

    is_highlight: bool = Field(default=False)
    photos: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="URLs of photos, max 5"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("photos")
    @classmethod
    def validate_photos_limit(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError("Maximum 5 photos allowed per interaction")
        return v

    class Settings:
        name = "interactions"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "contact_id": "uuid-here",
                "quick_summary": "Comimos juntos y hablamos sobre su nuevo trabajo",
                "emotion": "positivo",
                "topics": ["trabajo", "comida", "planes futuros"],
                "is_highlight": True,
            }
        }


class InteractionCreate(BaseModel):
    """Schema for creating a new interaction."""
    contact_id: str
    date: Optional[datetime] = None
    quick_summary: str = Field(..., min_length=1, max_length=500)
    emotion: EmotionType = EmotionType.POSITIVO
    topics: List[str] = Field(default_factory=list)
    is_highlight: bool = False


class InteractionUpdate(BaseModel):
    """Schema for updating an interaction."""
    date: Optional[datetime] = None
    quick_summary: Optional[str] = Field(None, min_length=1, max_length=500)
    emotion: Optional[EmotionType] = None
    topics: Optional[List[str]] = None
    is_highlight: Optional[bool] = None


class InteractionResponse(BaseModel):
    """Schema for interaction response."""
    interaction_id: str
    contact_id: str
    user_id: str
    contact_name: Optional[str] = None
    date: datetime
    quick_summary: str
    emotion: EmotionType
    emotion_emoji: str = ""
    topics: List[str]
    is_highlight: bool
    photos: List[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_interaction(
        cls,
        interaction: Interaction,
        contact_name: Optional[str] = None
    ) -> "InteractionResponse":
        """Create response from Interaction document."""
        return cls(
            interaction_id=interaction.interaction_id,
            contact_id=interaction.contact_id,
            user_id=interaction.user_id,
            contact_name=contact_name,
            date=interaction.date,
            quick_summary=interaction.quick_summary,
            emotion=interaction.emotion,
            emotion_emoji=EMOTION_EMOJIS.get(interaction.emotion, ""),
            topics=interaction.topics,
            is_highlight=interaction.is_highlight,
            photos=interaction.photos,
            created_at=interaction.created_at,
            updated_at=interaction.updated_at,
        )


class InteractionListResponse(BaseModel):
    """Schema for list of interactions response."""
    interactions: List[InteractionResponse]
    total: int
