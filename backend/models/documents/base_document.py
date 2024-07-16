import json
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass

import pydantic.dataclasses
from pydantic import BaseModel, validator, field_validator
from datetime import datetime


class DocumentMeta(BaseModel):
    source: str

    tags: list = []

    is_ai_generated: bool = False
    date_created: datetime = datetime.now()


class BaseDocument(BaseModel):
    document_meta: DocumentMeta

    @property
    def document_type(self):
        return self.__class__.__name__

    def to_json(self):
        return json.loads(self.model_dump_json())


class BaseTextDocument(BaseDocument):
    page_content: str

    def __init__(self, /, **data: Any):
        super().__init__(**data)
