from __future__ import annotations

import datetime
from functools import cache

import requests
import json
from os import PathLike
from typing import Optional

from backend.document_loader.base_document_loader import BaseDocumentLoader
from backend.document_loader.url_config import NseUrlConfig
from backend.models.documents import NseIndexDocument, NseIndexDocumentMeta

from tenacity import retry, stop_after_attempt, retry_if_result


def is_none_result(result):
    return result is None


def shrink_parameter(param_name):
    def _set_parameter(retry_state):
        components = retry_state.kwargs[param_name].split(" ")
        retry_state.kwargs[param_name] = " ".join(components[: len(components) - 1])

    return _set_parameter


class NseIndexLoader(BaseDocumentLoader[NseIndexDocument]):
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
        index: Optional[str] = "NIFTY 50",
        file_path: Optional[PathLike] = None,
        dataset: Optional[list[dict]] = None,
        tag_set: Optional[list] = None,
    ):
        self.index = index
        self.request_config = NseUrlConfig.get_index_config(index)
        self.file_path = file_path
        self.dataset = dataset
        super().__init__(tag_set)

        self.__initialize()

    def __initialize(self):
        if not self.dataset:
            if self.file_path:
                with open(self.file_path, "r") as file:
                    self.dataset = json.load(file)
            else:
                response = requests.get(**self.request_config)
                self.dataset = response.json()["data"]

        self._load_documents(self.dataset)

    def _load_documents(self, dataset: list[dict]):
        for doc in dataset:
            if "meta" in doc:
                metadata = NseIndexDocumentMeta(
                    source=self.request_config["url"],
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

    @staticmethod
    @cache
    @retry(stop=stop_after_attempt(5), reraise=True)
    def get_ticker_from_company_name(
        company_name: str,
        exchange: Optional[str] = "NSI",
        without_limited: Optional[bool] = False,
        without_hyphen: Optional[bool] = False,
    ) -> Optional[str]:
        """Get the ticker symbol given a company name from Yahoo Finance API."""

        if without_hyphen:
            company_name = company_name.replace("-", " ")

        if without_limited:
            possible_limited = [
                "LTD.",
                "LTD",
                "LIMITED.",
                "LIMITED",
                "PVT.",
                "PVT",
                "PRIVATE.",
                "PRIVATE",
            ]
            for limited in possible_limited:
                company_name = company_name.lower().replace(limited.lower(), "")

        ticker = None
        company_components = company_name.split(" ")
        num_components = len(company_components)

        while ticker is None and num_components > 0:
            company_name = " ".join(company_components[:num_components])
            ticker_finder_config = NseUrlConfig.get_yf_query_config(company_name)
            try:
                res = requests.get(**ticker_finder_config)
                data = res.json()
            except json.JSONDecodeError:
                return None

            company_code = data["quotes"]

            for company in company_code:
                if company["exchange"] == exchange:
                    ticker = company["symbol"]
                    break

            num_components -= 1

        return ticker

    @staticmethod
    def get_company_name_from_ticker(ticker: str) -> Optional[str]:
        company_finder_config = NseUrlConfig.get_yf_query_config(ticker)
        res = requests.get(**company_finder_config)
        data = res.json()

        company_code = data["quotes"]
        company_name = None

        for company in company_code:
            if company["symbol"] == ticker:
                if "longname" in company:
                    company_name = company["longname"]
                else:
                    company_name = company["shortname"]
                break

        return company_name

    def get_symbols(self):
        for symbol in self.iter_from_attrs("symbol"):
            yield symbol

    def get_company_names(self):
        for company_name in self.iter_from_attrs(["company_name"]):
            yield company_name
