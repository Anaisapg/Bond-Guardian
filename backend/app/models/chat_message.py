from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum


class SenderType(str, Enum):
    """Who sent the message."""
    USER = "user"
    BONDY = "bondy"


class MessageType(str, Enum):
    """Type of message."""
    TEXT = "text"
    ACTION_PREVIEW = "action_preview"
    SYSTEM = "system"


class ChatMode(str, Enum):
    """Chat conversation mode."""
    ACCION = "accion"
    CHARLA = "charla"
    ANALISIS = "analisis"


class ActionPreviewStatus(str, Enum):
    """Status of action preview."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class ActionPreview(BaseModel):
    """Preview of an action to be confirmed."""
    type: str  # reminder, interaction, contact, birthday
    data: Dict[str, Any] = Field(default_factory=dict)
    status: ActionPreviewStatus = ActionPreviewStatus.PENDING


class MessageMetadata(BaseModel):
    """Additional metadata for chat messages."""
    mode: ChatMode = ChatMode.CHARLA
    action_preview: Optional[ActionPreview] = None


class ChatMessage(Document):
    """Chat message document model."""
    message_id: Indexed(str, unique=True) = Field(default_factory=lambda: str(uuid4()))
    user_id: Indexed(str)

    sender: SenderType
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    message_type: MessageType = Field(default=MessageType.TEXT)
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)

    tokens_used: int = Field(default=0)

    class Settings:
        name = "chat_messages"
        use_state_management = True

    class Config:
        json_schema_extra = {
            "example": {
                "sender": "user",
                "content": "Bondy, quiero recordar llamar a mamá mañana",
                "message_type": "text",
            }
        }


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message."""
    content: str = Field(..., min_length=1, max_length=4000)
    mode: ChatMode = ChatMode.CHARLA


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    message_id: str
    sender: SenderType
    content: str
    timestamp: datetime
    message_type: MessageType
    metadata: MessageMetadata

    @classmethod
    def from_message(cls, message: ChatMessage) -> "ChatMessageResponse":
        """Create response from ChatMessage document."""
        return cls(
            message_id=message.message_id,
            sender=message.sender,
            content=message.content,
            timestamp=message.timestamp,
            message_type=message.message_type,
            metadata=message.metadata,
        )


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""
    messages: List[ChatMessageResponse]
    total: int
    has_more: bool = False


class ActionConfirmRequest(BaseModel):
    """Schema for confirming an action."""
    message_id: str
    confirmed: bool = True
