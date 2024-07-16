import datetime

from backend.models.documents.base_document import BaseDocument, DocumentMeta
from backend.models.documents.website_document import (
    WebsiteDocument,
    WebsiteDocumentMeta,
)
from backend.models.documents.faq_document import FaqDocumentMeta, FaqDocument


class TestDocument:

    def test_base_document(self, base_document_content):
        metadata = DocumentMeta(
            source=base_document_content.source,
            date_created=base_document_content.date_created,
        )
        document = BaseDocument(document_meta=metadata)
        document_json = document.to_json()

        assert document_json["document_meta"]["source"] == base_document_content.source
        assert document_json["document_meta"]["date_created"] == str(
            base_document_content.date_created.isoformat()
        )

    def test_website_document(self, webpage_content):
        metadata = WebsiteDocumentMeta(
            title=webpage_content.title,
            source=webpage_content.source,
            referrer_source=webpage_content.referrer_source,
            date_created=datetime.datetime.now(),
        )
        document = WebsiteDocument(
            page_content=webpage_content.page_content, document_meta=metadata
        )
        assert document.document_type == "WebsiteDocument"
        assert document.page_content == webpage_content.page_content
        json_doc = document.to_json()
        assert (
            json_doc["document_meta"]["referrer_source"]
            == webpage_content.referrer_source
        )

    def test_faq_document(self, faq_content):
        metadata = FaqDocumentMeta(
            title=faq_content.title,
            source=faq_content.source,
            date_created=datetime.datetime.now(),
        )
        document = FaqDocument(
            question=faq_content.question,
            answer=faq_content.answer,
            document_meta=metadata,
        )
        assert document.question == faq_content.question
        assert document.answer == faq_content.answer
        assert document.document_meta.title == faq_content.title
        json_doc = document.to_json()
        assert json_doc["question"] == faq_content.question
        assert json_doc["answer"] == faq_content.answer
        assert json_doc["document_meta"]["title"] == faq_content.title
