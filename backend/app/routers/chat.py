from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.chat_message import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
    ActionConfirmRequest,
    SenderType,
    MessageType,
    ChatMode,
    MessageMetadata,
    ActionPreview,
    ActionPreviewStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_bondy_response(
    user: User,
    user_message: str,
    mode: ChatMode,
    chat_history: List[ChatMessage],
) -> str:
    """
    Generate Bondy's response using Gemini AI.
    Falls back to predefined responses if Gemini is not available.
    """
    if settings.gemini_api_key:
        try:
            from app.services.gemini import generate_bondy_response
            response = await generate_bondy_response(
                user=user,
                user_message=user_message,
                mode=mode,
                chat_history=chat_history,
            )
            if response:
                return response
        except Exception as e:
            logger.warning(f"Gemini API error, using fallback: {e}")

    # Fallback responses based on mode
    bondy_name = user.bondy_config.name

    fallback_responses = {
        ChatMode.CHARLA: [
            f"¡Hola! Soy {bondy_name}, tu compañero para cuidar tus relaciones. ¿En qué puedo ayudarte hoy?",
            "Cuéntame más, estoy aquí para escucharte.",
            "Entiendo. ¿Hay algo específico que te gustaría hacer al respecto?",
        ],
        ChatMode.ACCION: [
            "¡Claro! Puedo ayudarte a crear recordatorios, registrar interacciones o añadir contactos. ¿Qué necesitas?",
            "Para crear un recordatorio, dime para quién, cuándo y el motivo.",
            "¿Te gustaría que te ayude a planificar algo?",
        ],
        ChatMode.ANALISIS: [
            "Analizando tus relaciones... ¿Sobre qué aspecto te gustaría que profundice?",
            "Puedo ver patrones en tus interacciones. ¿Quieres que te cuente más?",
            "Tus datos de relaciones me ayudan a darte mejores consejos. ¿Qué te gustaría saber?",
        ],
    }

    import random
    responses = fallback_responses.get(mode, fallback_responses[ChatMode.CHARLA])
    return random.choice(responses)


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
):
    """Send a message to Bondy and get a response."""
    try:
        # Save user message
        user_message = ChatMessage(
            user_id=current_user.user_id,
            sender=SenderType.USER,
            content=message_data.content,
            message_type=MessageType.TEXT,
            metadata=MessageMetadata(mode=message_data.mode),
        )
        await user_message.insert()

        # Get recent chat history for context
        recent_messages = await ChatMessage.find(
            ChatMessage.user_id == current_user.user_id
        ).sort(-ChatMessage.timestamp).limit(10).to_list()

        # Reverse to get chronological order
        recent_messages.reverse()

        # Generate Bondy's response
        response_content = await get_bondy_response(
            user=current_user,
            user_message=message_data.content,
            mode=message_data.mode,
            chat_history=recent_messages,
        )

        # Save Bondy's response
        bondy_message = ChatMessage(
            user_id=current_user.user_id,
            sender=SenderType.BONDY,
            content=response_content,
            message_type=MessageType.TEXT,
            metadata=MessageMetadata(mode=message_data.mode),
        )
        await bondy_message.insert()

        logger.info(f"Chat message processed for user {current_user.user_id}")

        return ChatMessageResponse.from_message(bondy_message)

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el mensaje"
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
):
    """Get chat history with Bondy."""
    try:
        total = await ChatMessage.find(
            ChatMessage.user_id == current_user.user_id
        ).count()

        messages = await ChatMessage.find(
            ChatMessage.user_id == current_user.user_id
        ).sort(-ChatMessage.timestamp).skip(offset).limit(limit).to_list()

        # Reverse to get chronological order
        messages.reverse()

        message_responses = [
            ChatMessageResponse.from_message(msg) for msg in messages
        ]

        has_more = offset + limit < total

        return ChatHistoryResponse(
            messages=message_responses,
            total=total,
            has_more=has_more,
        )

    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener el historial"
        )


@router.post("/action/confirm", response_model=ChatMessageResponse)
async def confirm_action(
    request: ActionConfirmRequest,
    current_user: User = Depends(get_current_user),
):
    """Confirm or cancel an action proposed by Bondy."""
    message = await ChatMessage.find_one(
        ChatMessage.message_id == request.message_id,
        ChatMessage.user_id == current_user.user_id,
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )

    if message.message_type != MessageType.ACTION_PREVIEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este mensaje no tiene una acción para confirmar"
        )

    if not message.metadata.action_preview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay acción pendiente en este mensaje"
        )

    try:
        bondy_name = current_user.bondy_config.name

        if request.confirmed:
            # Execute the action based on type
            action = message.metadata.action_preview
            action_type = action.type
            action_data = action.data

            result_message = ""

            if action_type == "reminder":
                from app.models.reminder import Reminder
                reminder = Reminder(
                    contact_id=action_data.get("contact_id"),
                    user_id=current_user.user_id,
                    reminder_date=datetime.fromisoformat(action_data.get("reminder_date")),
                    reason=action_data.get("reason"),
                    is_birthday=action_data.get("is_birthday", False),
                )
                await reminder.insert()
                result_message = f"¡Listo! He creado el recordatorio para ti."

            elif action_type == "interaction":
                from app.models.interaction import Interaction, EmotionType
                interaction = Interaction(
                    contact_id=action_data.get("contact_id"),
                    user_id=current_user.user_id,
                    quick_summary=action_data.get("quick_summary"),
                    emotion=EmotionType(action_data.get("emotion", "positivo")),
                    topics=action_data.get("topics", []),
                )
                await interaction.insert()
                result_message = f"¡Perfecto! He registrado la interacción."

            elif action_type == "contact":
                from app.models.contact import Contact
                contact = Contact(
                    user_id=current_user.user_id,
                    name=action_data.get("name"),
                    phone=action_data.get("phone"),
                    relationship_type=action_data.get("relationship_type", "amigo"),
                )
                await contact.insert()
                result_message = f"¡Genial! He añadido a {action_data.get('name')} a tus contactos."

            # Update action status
            message.metadata.action_preview.status = ActionPreviewStatus.CONFIRMED
            await message.save()

            # Create confirmation message
            confirmation = ChatMessage(
                user_id=current_user.user_id,
                sender=SenderType.BONDY,
                content=result_message,
                message_type=MessageType.SYSTEM,
                metadata=MessageMetadata(),
            )
            await confirmation.insert()

            return ChatMessageResponse.from_message(confirmation)

        else:
            # Cancel the action
            message.metadata.action_preview.status = ActionPreviewStatus.CANCELLED
            await message.save()

            cancel_message = ChatMessage(
                user_id=current_user.user_id,
                sender=SenderType.BONDY,
                content="Vale, he cancelado la acción. ¿Hay algo más en lo que pueda ayudarte?",
                message_type=MessageType.SYSTEM,
                metadata=MessageMetadata(),
            )
            await cancel_message.insert()

            return ChatMessageResponse.from_message(cancel_message)

    except Exception as e:
        logger.error(f"Error confirming action: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la acción"
        )


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    current_user: User = Depends(get_current_user),
):
    """Delete all chat history."""
    try:
        await ChatMessage.find(
            ChatMessage.user_id == current_user.user_id
        ).delete()

        logger.info(f"Chat history deleted for user {current_user.user_id}")

    except Exception as e:
        logger.error(f"Error deleting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al borrar el historial"
        )


@router.get("/search")
async def search_chat_history(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
):
    """Search through chat history."""
    try:
        messages = await ChatMessage.find(
            ChatMessage.user_id == current_user.user_id,
            {"content": {"$regex": query, "$options": "i"}},
        ).sort(-ChatMessage.timestamp).limit(limit).to_list()

        return {
            "results": [ChatMessageResponse.from_message(msg) for msg in messages],
            "total": len(messages),
            "query": query,
        }

    except Exception as e:
        logger.error(f"Error searching chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar en el historial"
        )
