from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.models.user import User, UserSettings, BondyConfig, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter()


class SettingsUpdateRequest(BaseModel):
    """Request body for updating settings."""
    settings: Optional[UserSettings] = None
    bondy_config: Optional[BondyConfig] = None


class SettingsResponse(BaseModel):
    """Response with all user settings."""
    settings: UserSettings
    bondy_config: BondyConfig


@router.get("", response_model=SettingsResponse)
async def get_settings(
    current_user: User = Depends(get_current_user),
):
    """Get current user's settings."""
    return SettingsResponse(
        settings=current_user.settings,
        bondy_config=current_user.bondy_config,
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    request: SettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update user's settings."""
    try:
        if request.settings:
            # Update individual fields to preserve defaults
            settings_data = request.settings.model_dump(exclude_unset=True)
            for field, value in settings_data.items():
                setattr(current_user.settings, field, value)

        if request.bondy_config:
            config_data = request.bondy_config.model_dump(exclude_unset=True)
            for field, value in config_data.items():
                setattr(current_user.bondy_config, field, value)

        current_user.updated_at = datetime.utcnow()
        await current_user.save()

        logger.info(f"Settings updated for user {current_user.user_id}")

        return SettingsResponse(
            settings=current_user.settings,
            bondy_config=current_user.bondy_config,
        )

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la configuración"
        )


@router.patch("/ritual-time")
async def update_ritual_time(
    ritual_time: str,
    current_user: User = Depends(get_current_user),
):
    """Update the preferred ritual time."""
    # Validate time format (HH:MM)
    try:
        hours, minutes = ritual_time.split(":")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError()
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de hora inválido. Usa HH:MM (ej: 09:00)"
        )

    current_user.settings.ritual_time = ritual_time
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"ritual_time": ritual_time}


@router.patch("/neglect-days")
async def update_neglect_days(
    days: int,
    current_user: User = Depends(get_current_user),
):
    """Update the number of days before a contact is considered neglected."""
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor debe estar entre 1 y 365 días"
        )

    current_user.settings.neglect_days = days
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"neglect_days": days}


@router.patch("/notifications")
async def update_notifications(
    enabled: bool,
    current_user: User = Depends(get_current_user),
):
    """Enable or disable push notifications."""
    current_user.settings.notifications_enabled = enabled
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"notifications_enabled": enabled}


@router.patch("/bondy-name")
async def update_bondy_name(
    name: str,
    current_user: User = Depends(get_current_user),
):
    """Update Bondy's custom name."""
    if len(name) < 1 or len(name) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre debe tener entre 1 y 20 caracteres"
        )

    current_user.bondy_config.name = name
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"bondy_name": name}


@router.patch("/coaching-level")
async def update_coaching_level(
    level: str,
    current_user: User = Depends(get_current_user),
):
    """Update the coaching intensity level."""
    valid_levels = ["activo", "moderado", "sutil"]

    if level not in valid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nivel inválido. Opciones: {', '.join(valid_levels)}"
        )

    current_user.settings.coaching_level = level
    current_user.bondy_config.coaching_level = level
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"coaching_level": level}


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile."""
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        picture=current_user.picture,
        auth_provider=current_user.auth_provider,
        settings=current_user.settings,
        bondy_config=current_user.bondy_config,
        created_at=current_user.created_at,
    )


@router.patch("/profile")
async def update_profile(
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Update user's profile."""
    if name:
        if len(name) < 1 or len(name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre debe tener entre 1 y 100 caracteres"
            )
        current_user.name = name

    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    return {"name": current_user.name}
