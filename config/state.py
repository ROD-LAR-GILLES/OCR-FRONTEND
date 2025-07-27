"""
Estado temporal para compatibilidad durante la refactorización.
Este módulo proporciona compatibilidad con versiones anteriores
mientras se completa la migración a la nueva arquitectura.

DEPRECATED: 
    Este módulo está marcado para eliminación en futuras versiones.
    Por favor, use src.shared.constants.config.AppConfig en su lugar.
    Ver docs/MIGRATION.md para más información sobre la migración.
"""
import warnings
from src.shared.constants.config import AppConfig

# Emitir advertencia de deprecación
warnings.warn(
    "El módulo config.state está obsoleto y será eliminado en futuras versiones. "
    "Use src.shared.constants.config.AppConfig en su lugar.",
    DeprecationWarning, stacklevel=2
)

# Instancia de configuración centralizada
app_config = AppConfig()

# Variables de estado (mantienen compatibilidad con código antiguo)
ocr_engine = None
llm_provider = None
current_document = None

# Variables para configuración OCR (sincronizadas con AppConfig)
OCR_DPI = app_config.ocr.dpi
OCR_LANG = app_config.ocr.language
OCR_PSM = app_config.ocr.psm
OCR_OEM = app_config.ocr.oem
OCR_TIMEOUT = 60

# Variables para configuración LLM
LLM_MODE = 'prompt'
LLM_PROVIDER = None
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 500
LLM_TIMEOUT = 30
