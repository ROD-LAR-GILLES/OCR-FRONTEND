"""
Adaptadores compartidos para la API.
"""
from infrastructure.storage_adapter import StorageAdapter
from infrastructure.document_adapter import DocumentAdapter

# Instancias globales de los adaptadores
storage_adapter = StorageAdapter()
document_adapter = DocumentAdapter()
