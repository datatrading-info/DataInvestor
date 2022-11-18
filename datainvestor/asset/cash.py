from datainvestor.asset.asset import Asset


class Cash(Asset):
    """
    Memorizza i metadati di un asset Cash.

    Parameters
    ----------
    currency : str, optional
        La valuta del Cash Asset. Il valore predefinito è USD.
    """

    def __init__(
        self,
        currency='USD'
    ):
        self.cash_like = True
        self.currency = currency
