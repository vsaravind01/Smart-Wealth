from datetime import datetime
from typing import Optional

from pydantic import HttpUrl

from backend.models.documents import BaseDocument, BaseDocumentMeta


class NseIndexDocumentMeta(BaseDocumentMeta):
    open: float
    day_high: float
    day_low: float
    year_high: float
    year_low: float
    last_price: float
    change: float
    percentage_change: float
    last_updated_time: datetime

    previous_close: Optional[float]
    total_traded_volume: Optional[float]
    percentage_change_365: Optional[float]
    percentage_change_30: Optional[float]

    chart_day_img_path: HttpUrl
    chart_365_img_path: HttpUrl
    chart_30_img_path: HttpUrl


class NseIndexDocument(BaseDocument):
    symbol: str
    document_meta: NseIndexDocumentMeta

    company_name: Optional[str]
    industry: Optional[str]
    isin: Optional[str]
