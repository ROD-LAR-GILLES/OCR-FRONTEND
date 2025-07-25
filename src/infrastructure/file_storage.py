"""
Módulo de infraestructura encargado del almacenamiento de resultados del procesamiento OCR de archivos PDF.

Este módulo define funciones para guardar el contenido extraído en formato Markdown. Los archivos generados
se escriben en el directorio `resultado/`, utilizando como nombre base el del archivo PDF procesado.

También maneja el almacenamiento de logs de las interacciones con la API de OpenAI y el estado de las
conversaciones para propósitos de auditoría, debugging y continuidad de contexto.

Pertenece a la capa de infraestructura en la arquitectura limpia, y se comunica con la capa de dominio a través
de interfaces definidas. No contiene lógica de negocio, solo responsabilidades técnicas relacionadas al sistema
de archivos.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger

# Directorios de trabajo
OUTPUT_DIR = Path("resultado")
LOGS_DIR = Path("logs")
API_LOGS_DIR = LOGS_DIR / "api_calls"
CONVERSATIONS_DIR = LOGS_DIR / "conversations"

# Estructura de una conversación
Conversation = List[Dict[str, str]]


def save_markdown(stem: str, markdown: str) -> Path:
    """
    Guarda el contenido Markdown como archivo `.md` en el directorio de salida.

    Args:
        stem (str): Nombre base del archivo sin extensión.
        markdown (str): Contenido en formato Markdown a escribir.

    Returns:
        Path: Ruta absoluta del archivo `.md` generado.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    md_path = OUTPUT_DIR / f"{stem}.md"
    md_path.write_text(markdown, encoding="utf-8")
    logger.info(f"Markdown guardado en {md_path}")
    return md_path

def log_api_interaction(
    model: str,
    messages: list[Dict[str, str]],
    response: Any,
    error: Exception | None = None,
    conversation_id: Optional[str] = None
) -> Path:
    """
    Guarda un registro detallado de la interacción con la API de OpenAI.

    Args:
        model: El modelo usado (ej: 'gpt-4', 'gpt-3.5-turbo')
        messages: Lista de mensajes enviados a la API
        response: Respuesta de la API o None si hubo error
        error: Excepción capturada si hubo error
        conversation_id: ID de la conversación si es parte de una secuencia

    Returns:
        Path: Ruta al archivo de log generado
    """
    API_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Crear nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = API_LOGS_DIR / f"api_call_{timestamp}.json"
    
    # Preparar datos del log
    log_data = {
        "timestamp": timestamp,
        "model": model,
        "messages": messages,
        "success": error is None,
        "conversation_id": conversation_id
    }
    
    # Agregar respuesta o error según el caso
    if error:
        log_data["error"] = {
            "type": type(error).__name__,
            "message": str(error)
        }
    else:
        # Convertir la respuesta de la API a dict si es necesario
        log_data["response"] = response.model_dump() if hasattr(response, 'model_dump') else str(response)
    
    # Guardar log
    log_file.write_text(json.dumps(log_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.debug(f"Log de API guardado en {log_file}")
    
    # Si es parte de una conversación, actualizar el historial
    if conversation_id and not error:
        update_conversation_history(conversation_id, messages, response)
    
    return log_file

def load_conversation(conversation_id: str) -> Optional[Conversation]:
    """
    Carga el historial de una conversación existente.
    
    Args:
        conversation_id: Identificador único de la conversación
    
    Returns:
        Optional[Conversation]: Lista de mensajes de la conversación o None si no existe
    """
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    conv_file = CONVERSATIONS_DIR / f"{conversation_id}.json"
    
    if not conv_file.exists():
        return None
        
    try:
        return json.loads(conv_file.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Error al cargar conversación {conversation_id}: {e}")
        return None

def update_conversation_history(
    conversation_id: str,
    new_messages: List[Dict[str, str]],
    response: Any
) -> None:
    """
    Actualiza el historial de una conversación con nuevos mensajes.
    
    Args:
        conversation_id: Identificador único de la conversación
        new_messages: Nuevos mensajes a agregar
        response: Respuesta de la API
    """
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)
    conv_file = CONVERSATIONS_DIR / f"{conversation_id}.json"
    
    # Cargar historial existente o crear nuevo
    history = load_conversation(conversation_id) or []
    
    # Agregar nuevos mensajes
    history.extend(new_messages)
    
    # Agregar respuesta del asistente
    if hasattr(response, 'choices') and response.choices:
        history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })
    
    # Guardar historial actualizado
    conv_file.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )