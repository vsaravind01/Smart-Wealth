import json
from typing import Any

from pydantic import BaseModel
from datetime import datetime


class BaseDocumentMeta(BaseModel):
    source: str

    tags: list = []

    is_ai_generated: bool = False
    date_created: datetime = datetime.now()

    def to_json(self):
        return json.loads(self.model_dump_json())


class BaseDocument(BaseModel):
    document_meta: BaseDocumentMeta

    @property
    def document_type(self):
        return self.__class__.__name__

    def to_json(self):
        return json.loads(self.model_dump_json())


class BaseTextDocument(BaseDocument):
    page_content: str

    def __init__(self, /, **data: Any):
        super().__init__(**data)

    def format_document(self):
        raise NotImplementedError()
