from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass

import pytest


@dataclass
class BaseDocumentContent:
    source = "https://sample_source.com"
    date_created = datetime.now()


@dataclass
class WebPageContent(BaseDocumentContent):
    page_content = (
        "sample document with multiple lines."
        "With another line."
        "No worries, will stop here."
    )
    title = "sample title"
    referrer_source = "https://referrer.com"


@dataclass
class FaqContent(BaseDocumentContent):
    title = "Faq page title"
    question = "So, this supposed to be a question? Is it though?"
    answer = "I guess so."


@pytest.fixture
def base_document_content() -> BaseDocumentContent:
    return BaseDocumentContent()


@pytest.fixture
def webpage_content() -> WebPageContent:
    return WebPageContent()


@pytest.fixture
def faq_content() -> FaqContent:
    return FaqContent()
