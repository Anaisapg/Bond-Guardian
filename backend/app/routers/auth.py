from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import logging

from app.core.security import create_access_token, get_current_user
from app.models.user import User, UserCreate, UserResponse, UserSettings, BondyConfig
from app.models.ritual_streak import RitualStreak

logger = logging.getLogger(__name__)
router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Request body for Google OAuth."""
    id_token: str


class TokenResponse(BaseModel):
    """Response with access token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class SessionDataRequest(BaseModel):
    """Request body for session data processing."""
    session_id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google OAuth.

    In production, this would verify the id_token with Google.
    For now, we'll use a simplified flow for development.
    """
    # TODO: In production, verify the token with Google:
    # from google.oauth2 import id_token
    # from google.auth.transport import requests
    # idinfo = id_token.verify_oauth2_token(request.id_token, requests.Request(), GOOGLE_CLIENT_ID)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth requires proper configuration. Use /session-data for development."
    )


@router.post("/session-data", response_model=TokenResponse)
async def process_session_data(request: SessionDataRequest):
    """
    Process session data and create/update user.

    This endpoint is used after Google OAuth callback.
    Creates a new user if they don't exist, or returns existing user.
    """
    try:
        # Check if user already exists
        existing_user = await User.find_one(User.email == request.email)

        if existing_user:
            # Update user info if needed
            existing_user.name = request.name
            if request.picture:
                existing_user.picture = request.picture
            existing_user.updated_at = datetime.utcnow()
            await existing_user.save()

            user = existing_user
            logger.info(f"User logged in: {user.email}")
        else:
            # Create new user
            user = User(
                email=request.email,
                name=request.name,
                picture=request.picture,
                auth_provider="google",
                settings=UserSettings(),
                bondy_config=BondyConfig(),
            )
            await user.insert()

            # Create initial ritual streak for new user
            streak = RitualStreak(user_id=user.user_id)
            await streak.insert()

            logger.info(f"New user created: {user.email}")

        # Create access token
        access_token = create_access_token(data={"sub": user.user_id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse(
                user_id=user.user_id,
                email=user.email,
                name=user.name,
                picture=user.picture,
                auth_provider=user.auth_provider,
                settings=user.settings,
                bondy_config=user.bondy_config,
                created_at=user.created_at,
            )
        )

    except Exception as e:
        logger.error(f"Error processing session data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar la autenticación"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
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


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.

    Note: JWT tokens are stateless, so we can't truly invalidate them.
    The client should discard the token.
    """
    return {"message": "Sesión cerrada correctamente"}


# Development-only endpoint for testing
@router.post("/dev/create-test-user", response_model=TokenResponse)
async def create_test_user():
    """
    Create a test user for development.

    This endpoint should be disabled in production.
    """
    test_email = "test@bondguardian.dev"

    # Check if test user exists
    existing_user = await User.find_one(User.email == test_email)

    if existing_user:
        # Delete and recreate for fresh start
        await existing_user.delete()

        # Also delete associated streak
        streak = await RitualStreak.find_one(RitualStreak.user_id == existing_user.user_id)
        if streak:
            await streak.delete()

    # Create test user
    user = User(
        email=test_email,
        name="Usuario de Prueba",
        picture=None,
        auth_provider="google",
        settings=UserSettings(),
        bondy_config=BondyConfig(),
    )
    await user.insert()

    # Create ritual streak
    streak = RitualStreak(user_id=user.user_id)
    await streak.insert()

    # Create access token
    access_token = create_access_token(data={"sub": user.user_id})

    logger.info(f"Test user created: {user.email}")

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            auth_provider=user.auth_provider,
            settings=user.settings,
            bondy_config=user.bondy_config,
            created_at=user.created_at,
        )
    )
