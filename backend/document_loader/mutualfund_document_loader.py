import json

from backend.document_loader import BaseDocumentLoader
from backend.models.documents.tags import mutualfund_tag_map
from backend.models.documents import MutualFundDocument, MutualFundDocumentMeta


class MutualFundDocumentLoader(BaseDocumentLoader[MutualFundDocument]):
    def __init__(
        self, file_path: str, mutual_fund_source: str, tag_set: list[str] = None
    ):
        self.file_path = file_path
        self.mutual_fund_source = mutual_fund_source
        if not tag_set:
            tag_set = list(mutualfund_tag_map.keys())
        tag_map = mutualfund_tag_map

        super().__init__(tag_set=tag_set, tag_map=tag_map)

        self._initialize()

    def _initialize(self):
        with open(self.file_path, "r") as file:
            ds = json.load(file)
            self._load_dataset(ds)

    def _load_dataset(self, dataset: list[dict]):
        for doc in dataset:
            metadata = MutualFundDocumentMeta(
                source=self.mutual_fund_source,
                fund_name=doc["Fund Name"],
                investment_objective=doc["Investment Objective"],
                scheme_riskometer=doc["Scheme Riskometer"],
                portfolio=doc["Portfolio"],
                market_capitalization=doc["Market Capitalization"],
                sectoral_composition=doc["Sectoral Composition"],
                expense_ratio_and_quantitative_data=doc[
                    "Expense Ratio & Quantitative Data"
                ],
                key_statistics=doc["Key Statistics"],
                load_structure=doc["Load Structure"],
                minimum_investment_amount=doc["Minimum Investment Amount"],
                fund_manager=doc["Fund Manager"],
                composition_by_assets=doc["Composition by Assets"],
                credit_quality_profile=(
                    doc["Credit Quality Profile"]
                    if doc["Credit Quality Profile"] not in ["null", "nil"]
                    else None
                ),
            )
            document = MutualFundDocument(document_meta=metadata)
            self.documents.append(document)
