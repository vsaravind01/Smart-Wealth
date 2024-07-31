class NseUrlConfig:
    indices = ["NIFTY 50"]

    @staticmethod
    def get_index_config(index: str):
        index_config = {
            "url": f"https://www.nseindia.com/api/equity-stockIndices?index={index}",
            "headers": {
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "DNT": "1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/79.0.3945.79 Safari/537.36",
                "Sec-Fetch-User": "?1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*"
                "/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
            },
        }
        return index_config

    @staticmethod
    def get_yf_query_config(query: str):
        return {
            "url": "https://query2.finance.yahoo.com/v1/finance/search",
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            "params": {"q": query, "quotes_count": 1},
        }
