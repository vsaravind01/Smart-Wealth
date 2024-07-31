from typing import Any, Optional

from backend.models.documents import BaseDocument, BaseDocumentMeta


class MutualFundDocumentMeta(BaseDocumentMeta):
    fund_name: str
    investment_objective: str
    scheme_riskometer: str
    portfolio: dict[str, Any]
    expense_ratio_and_quantitative_data: dict[str, Any]
    load_structure: dict[str, Any]
    minimum_investment_amount: dict[str, Any]
    fund_manager: dict[str, Any]

    key_statistics: Optional[dict[str, Any]] = None
    market_capitalization: Optional[dict[str, Any]] = None
    sectoral_composition: Optional[dict[str, Any]]
    composition_by_assets: Optional[dict[str, Any]] = None
    credit_quality_profile: Optional[dict[str, Any]] = None

    tickers: Optional[list[str]] = None


class MutualFundDocument(BaseDocument):
    document_meta: MutualFundDocumentMeta

    def __init__(self, /, **data: Any):
        super().__init__(**data)
