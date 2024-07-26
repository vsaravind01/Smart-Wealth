from backend.models.documents import NewsDocument, ExpertDocument, WebsiteDocument

container_to_document_map = {
    "stock-news": NewsDocument,
    "expert-news": ExpertDocument,
    "bob-web": WebsiteDocument,
}
