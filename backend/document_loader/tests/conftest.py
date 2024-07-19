import pytest
import requests

from backend.document_loader.url_config import NseUrlConfig


@pytest.fixture
def nse_index_data() -> list[dict]:
    config = NseUrlConfig.get_index_config("NIFTY 50")
    response = requests.get(**config)
    return response.json()["data"]
