from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List
from datetime import datetime
import logging

from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.contact import Contact
from app.models.interaction import Interaction

logger = logging.getLogger(__name__)
router = APIRouter()

# Valid image types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> bool:
    """Validate that the file is an allowed image type."""
    if not file.filename:
        return False

    extension = file.filename.split(".")[-1].lower()
    return extension in ALLOWED_EXTENSIONS


async def upload_to_cloudinary(
    file: UploadFile,
    folder: str,
) -> str:
    """Upload a file to Cloudinary and return the URL."""
    if not all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Cloudinary no está configurado. Configura las variables de entorno."
        )

    try:
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
        )

        # Read file content
        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo es demasiado grande. Máximo 5MB."
            )

        # Upload with transformation
        result = cloudinary.uploader.upload(
            content,
            folder=folder,
            transformation={
                "width": 500,
                "height": 500,
                "crop": "fill",
                "quality": "auto",
                "fetch_format": "auto",
            },
        )

        return result["secure_url"]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la imagen"
        )


async def delete_from_cloudinary(photo_url: str) -> bool:
    """Delete a photo from Cloudinary."""
    if not all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
        return False

    try:
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
        )

        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/{cloud}/image/upload/v{version}/{folder}/{public_id}.{ext}
        parts = photo_url.split("/")
        public_id_with_ext = "/".join(parts[-2:])  # folder/filename
        public_id = public_id_with_ext.rsplit(".", 1)[0]

        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"

    except Exception as e:
        logger.error(f"Cloudinary delete error: {e}")
        return False


@router.post("/contacts/{contact_id}/photo")
async def upload_contact_photo(
    contact_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload a profile photo for a contact."""
    # Validate contact ownership
    contact = await Contact.find_one(
        Contact.contact_id == contact_id,
        Contact.user_id == current_user.user_id,
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contacto no encontrado"
        )

    # Validate file
    if not validate_image(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagen no válido. Usa JPG, PNG o WebP."
        )

    try:
        # Delete old photo if exists
        if contact.photo_url:
            await delete_from_cloudinary(contact.photo_url)

        # Upload new photo
        folder = f"bond-guardian/contacts/{current_user.user_id}"
        photo_url = await upload_to_cloudinary(file, folder)

        # Update contact
        contact.photo_url = photo_url
        contact.updated_at = datetime.utcnow()
        await contact.save()

        logger.info(f"Photo uploaded for contact {contact.name}")

        return {"photo_url": photo_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading contact photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir la foto"
        )


@router.post("/interactions/{interaction_id}/photos")
async def upload_interaction_photos(
    interaction_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload photos to an interaction (max 5 total)."""
    # Validate interaction ownership
    interaction = await Interaction.find_one(
        Interaction.interaction_id == interaction_id,
        Interaction.user_id == current_user.user_id,
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interacción no encontrada"
        )

    # Check total photos limit
    current_count = len(interaction.photos)
    if current_count + len(files) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo 5 fotos por interacción. Ya tienes {current_count}."
        )

    # Validate all files
    for file in files:
        if not validate_image(file):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato no válido: {file.filename}. Usa JPG, PNG o WebP."
            )

    try:
        folder = f"bond-guardian/interactions/{current_user.user_id}"
        uploaded_urls = []

        for file in files:
            photo_url = await upload_to_cloudinary(file, folder)
            uploaded_urls.append(photo_url)

        # Update interaction
        interaction.photos.extend(uploaded_urls)
        interaction.updated_at = datetime.utcnow()
        await interaction.save()

        logger.info(f"Photos uploaded for interaction {interaction_id}")

        return {
            "photos": interaction.photos,
            "uploaded": uploaded_urls,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading interaction photos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al subir las fotos"
        )


@router.delete("")
async def delete_photo(
    photo_url: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a photo from a contact or interaction."""
    try:
        # Check if it's a contact photo
        contact = await Contact.find_one(
            Contact.user_id == current_user.user_id,
            Contact.photo_url == photo_url,
        )

        if contact:
            await delete_from_cloudinary(photo_url)
            contact.photo_url = None
            contact.updated_at = datetime.utcnow()
            await contact.save()
            return {"message": "Foto eliminada del contacto"}

        # Check if it's an interaction photo
        interaction = await Interaction.find_one(
            Interaction.user_id == current_user.user_id,
            {"photos": photo_url},
        )

        if interaction:
            await delete_from_cloudinary(photo_url)
            interaction.photos.remove(photo_url)
            interaction.updated_at = datetime.utcnow()
            await interaction.save()
            return {"message": "Foto eliminada de la interacción"}

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foto no encontrada"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar la foto"
        )
