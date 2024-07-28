from enum import Enum


class SourceMap(Enum):
    """Map of source to the type of document"""

    LOAN = "loan"
    INSURANCE = "insurance"
    GOVT_DEPOSIT_SCHEME = "govt-deposit-scheme"
    TERM_DEPOSIT = "term-deposit"
    CARD = "card"
    ACCOUNT = "account"
    DEMAT = "demat"
    MUTUAL_FUND = "mutual-fund"
    FAQ = "faq"

    def __contains__(self, item):
        return item in self.__class__.__members__.values()

    @property
    def url_prefix(self):
        return {
            "loan": "https://www.bankofbaroda.in/personal-banking/loans",
            "insurance": "https://www.bankofbaroda.in/personal-banking/insurance",
            "govt-deposit-scheme": "https://www.bankofbaroda.in/personal-banking/investments/government-deposit-schemes",
            "term-deposit": "https://www.bankofbaroda.in/personal-banking/accounts/term-deposit",
            "card": "https://www.bankofbaroda.in/personal-banking/digital-products/cards",
            "account": "https://www.bankofbaroda.in/personal-banking/accounts",
            "demat": "https://www.bankofbaroda.in/personal-banking/investments/investment-products/demat",
            "mutual-fund": "https://www.bankofbaroda.in/personal-banking/investments/investment-products/mutual-fund",
            "faq": "https://www.bankofbaroda.in/faqs",
        }[self.value]
