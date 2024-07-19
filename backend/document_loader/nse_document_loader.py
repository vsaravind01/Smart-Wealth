from __future__ import annotations

import datetime
import requests
import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseDataLoader
from backend.document_loader.url_config import NseUrlConfig
from backend.models.documents import NseIndexDocument, NseIndexDocumentMeta


class NseIndexLoader(BaseDataLoader):
    """Document Loader for NSE Index API.
    The class expects either a json file_path or dataset as list of dictionaries.

    Attributes:
    -----------
    source: str
        The source of the documents
    file_path: Optional[PathLike]
        The path of the json document to load from
    dataset: Optional[list[dict]]
        The dataset as list of dictionaries
    tag_set:
    """

    def __init__(
        self,
        source: str,
        file_path: Optional[PathLike] = None,
        dataset: Optional[list[dict]] = None,
        tag_set: Optional[list] = None,
    ):
        self.source = source
        self.file_path = file_path
        self.dataset = dataset
        super().__init__(tag_set)

        self.__initialize()

    def __initialize(self, index: str = "NIFTY 50"):
        if not self.dataset:
            if self.file_path:
                with open(self.file_path, "r") as file:
                    self.dataset = json.load(file)
            else:
                config = NseUrlConfig.get_index_config(index)
                response = requests.get(**config)
                self.dataset = response.json()["data"]

        self._load_documents(self.dataset)

    def _load_documents(self, dataset: list[dict]):
        for doc in dataset:
            if "meta" in doc:
                metadata = NseIndexDocumentMeta(
                    source=self.source,
                    open=doc["open"],
                    day_high=doc["dayHigh"],
                    day_low=doc["dayLow"],
                    year_high=doc["yearHigh"],
                    year_low=doc["yearLow"],
                    last_price=doc["lastPrice"],
                    change=doc["change"],
                    percentage_change=doc["pChange"],
                    last_updated_time=datetime.datetime.strptime(
                        doc["lastUpdateTime"], "%d-%b-%Y %H:%M:%S"
                    ),
                    previous_close=doc["previousClose"],
                    total_traded_volume=doc["totalTradedVolume"],
                    percentage_change_365=doc["perChange365d"],
                    percentage_change_30=doc["perChange30d"],
                    chart_day_img_path=doc["chartTodayPath"],
                    chart_365_img_path=doc["chart365dPath"],
                    chart_30_img_path=doc["chart30dPath"],
                )
                document = NseIndexDocument(
                    symbol=doc["symbol"],
                    company_name=doc["meta"]["companyName"],
                    industry=doc["meta"].get("industry", "NA"),
                    isin=doc["meta"]["isin"],
                    document_meta=metadata,
                )
                self.documents.append(document)

    def get_symbols(self):
        for symbol in self.iter_from_attrs("symbol"):
            yield symbol

    def get_company_names(self):
        for company_name in self.iter_from_attrs(["company_name"]):
            yield company_name
