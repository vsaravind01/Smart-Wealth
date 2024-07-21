from backend.document_loader.base_document_loader import BaseDocumentLoader
from typing import TypeVar

BaseDocumentLoaderType = TypeVar("BaseDocumentLoaderType", bound=BaseDocumentLoader)

__all__ = ["BaseDocumentLoader"]
