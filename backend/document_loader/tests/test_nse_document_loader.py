from backend.document_loader.nse_document_loader import NseIndexLoader


class TestNseIndexDocumentLoader:
    def test_nse_index_document_loader_auto(self):
        loader = NseIndexLoader()
        assert loader.documents != []
        assert hasattr(loader.documents[0], "symbol")

    def test_nse_index_document_loader_dataset(self, nse_index_data):
        loader = NseIndexLoader(dataset=nse_index_data)
        assert loader.documents != []
        assert hasattr(loader.documents[0], "symbol")

    def test_nse_index_get_symbols(self):
        loader = NseIndexLoader()
        for symbol in loader.get_symbols():
            assert isinstance(symbol, str)

    def test_nse_index_get_companies(self, nse_index_data):
        loader = NseIndexLoader(dataset=nse_index_data)
        for company_name in loader.get_company_names():
            assert isinstance(company_name, str)
