import google.generativeai as genai
from typing import Optional, List
from datetime import datetime
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None


async def generate_person_context(contact, user) -> Optional[str]:
    """
    Generate context for reconnecting with a contact.

    Args:
        contact: Contact document
        user: User document

    Returns:
        Generated context string or None if failed
    """
    if not model:
        return None

    days_since = None
    if contact.last_interaction_date:
        days_since = (datetime.utcnow() - contact.last_interaction_date).days

    prompt = f"""
Eres un asistente que ayuda a mantener relaciones personales.

Contacto: {contact.name}, relación: {contact.relationship_type}
Última interacción: {"hace " + str(days_since) + " días" if days_since else "nunca registrada"}
Resumen última conversación: {contact.last_interaction_summary or "No disponible"}
Notas sobre el contacto: {contact.notes or "Sin notas"}

Genera un contexto breve (máx 100 palabras) que ayude al usuario a reconectar con esta persona.
Debe ser cálido, natural y específico. Si hay temas previos, mencionarlos sutilmente.
Usa español natural de España.
No uses frases robóticas ni demasiado formales.
"""

    try:
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini error generating context: {e}")
        return None


async def generate_insights(
    total_contacts: int,
    recent_interactions: int,
    neglected_count: int,
    user,
) -> Optional[List[str]]:
    """
    Generate insights about user's relationships.

    Args:
        total_contacts: Total number of contacts
        recent_interactions: Number of interactions in the last week
        neglected_count: Number of neglected contacts
        user: User document

    Returns:
        List of insight strings or None if failed
    """
    if not model:
        return None

    prompt = f"""
Analiza estos datos de relaciones personales:

Total contactos: {total_contacts}
Interacciones última semana: {recent_interactions}
Contactos descuidados (más de {user.settings.neglect_days} días sin contacto): {neglected_count}

Genera 3 insights útiles y accionables sobre cómo el usuario puede mejorar
sus relaciones. Sé específico, empático y constructivo.

Formato: Devuelve SOLO un JSON array con 3 strings, sin explicación adicional.
Ejemplo: ["Insight 1", "Insight 2", "Insight 3"]

Usa español natural de España.
"""

    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()

        # Try to parse as JSON
        if text.startswith("["):
            insights = json.loads(text)
            if isinstance(insights, list) and len(insights) >= 1:
                return insights[:3]

        # Fallback: split by newlines
        lines = [line.strip().lstrip("0123456789.-) ") for line in text.split("\n") if line.strip()]
        return lines[:3]

    except Exception as e:
        logger.error(f"Gemini error generating insights: {e}")
        return None


async def generate_bondy_response(
    user,
    user_message: str,
    mode: str,
    chat_history: list,
) -> Optional[str]:
    """
    Generate Bondy's chat response.

    Args:
        user: User document
        user_message: The user's message
        mode: Chat mode (accion, charla, analisis)
        chat_history: Recent chat messages

    Returns:
        Bondy's response string or None if failed
    """
    if not model:
        return None

    bondy_name = user.bondy_config.name
    coaching_level = user.bondy_config.coaching_level
    user_gender = user.settings.gender_preference

    # Format chat history
    history_text = ""
    for msg in chat_history[-10:]:
        sender = "Usuario" if msg.sender.value == "user" else bondy_name
        history_text += f"{sender}: {msg.content}\n"

    coaching_styles = {
        "activo": "Haz preguntas profundas y guía la conversación. Sé proactivo en dar consejos.",
        "moderado": "Equilibra entre escuchar y aconsejar. Pregunta cuando sea relevante.",
        "sutil": "Principalmente escucha y responde. Da consejos solo si se te piden.",
    }

    gender_pronouns = {
        "masculino": "él/lo",
        "femenino": "ella/la",
        "neutro": "tú",
        "no_especificado": "tú",
    }

    system_prompt = f"""
Eres {bondy_name}, el asistente personal de {user.name}.

PERSONALIDAD:
- Rol: Compañero empático y consejero de relaciones
- Tono: Cálido, cercano, empático
- Idioma: Español natural de España (evita anglicismos y traducciones literales)
- Pronombres para el usuario: {gender_pronouns.get(user_gender, "tú")}
- Emojis: Usa de forma natural pero sin exceso (1-2 por mensaje máximo)

ESTILO SEGÚN NIVEL DE COACHING:
{coaching_styles.get(coaching_level, coaching_styles["moderado"])}

MODO ACTUAL: {mode}
- accion: El usuario quiere hacer algo (crear recordatorio, registrar interacción, etc.)
- charla: Conversación casual, desahogo, reflexión
- analisis: El usuario quiere analizar sus relaciones o recibir insights

HISTORIAL RECIENTE:
{history_text if history_text else "Sin mensajes previos"}

INSTRUCCIONES CRÍTICAS:
1. NUNCA uses frases frías o robóticas como "Procesando...", "Operación exitosa", "Entendido"
2. Habla como un amigo empático, no como un robot
3. Respuestas concisas (máximo 150 palabras) pero cálidas
4. Si el usuario menciona crear algo (recordatorio, interacción), confirma que lo entendiste y pregunta detalles si faltan
5. Usa fechas relativas cuando sea natural ("mañana", "la semana que viene")
6. Si no estás seguro de algo, pregunta para aclarar

USUARIO DICE: {user_message}

Responde como {bondy_name} (solo el texto de respuesta, sin prefijo):
"""

    try:
        response = await model.generate_content_async(system_prompt)
        text = response.text.strip()

        # Remove any accidental prefix
        if text.startswith(f"{bondy_name}:"):
            text = text[len(f"{bondy_name}:"):].strip()

        return text

    except Exception as e:
        logger.error(f"Gemini error generating Bondy response: {e}")
        return None


async def detect_action_intent(user_message: str) -> Optional[dict]:
    """
    Detect if the user wants to perform an action (create reminder, log interaction, etc.)

    Args:
        user_message: The user's message

    Returns:
        Dict with action type and extracted data, or None
    """
    if not model:
        return None

    prompt = f"""
Analiza este mensaje del usuario y detecta si quiere realizar alguna acción:

Mensaje: "{user_message}"

Acciones posibles:
- reminder: Crear un recordatorio (ej: "recuérdame llamar a mamá mañana")
- interaction: Registrar una interacción (ej: "hoy comí con Juan y hablamos de su trabajo")
- contact: Añadir un contacto (ej: "añade a María como amiga")

Si detectas una acción, responde SOLO con un JSON en este formato:
{{"action": "tipo_accion", "data": {{"campo1": "valor1"}}}}

Si no detectas ninguna acción clara, responde: null

Ejemplos de respuestas:
- Para "recuérdame llamar a Ana el viernes": {{"action": "reminder", "data": {{"contact_name": "Ana", "date": "viernes", "reason": "llamar"}}}}
- Para "hoy desayuné con Pedro": {{"action": "interaction", "data": {{"contact_name": "Pedro", "summary": "desayunamos juntos"}}}}
- Para "qué tal estás": null

Responde SOLO el JSON o null, sin explicación.
"""

    try:
        response = await model.generate_content_async(prompt)
        text = response.text.strip()

        if text.lower() == "null":
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    except Exception as e:
        logger.error(f"Gemini error detecting action: {e}")
        return None
