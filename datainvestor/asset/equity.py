from datainvestor.asset.asset import Asset


class Equity(Asset):
    """
        Memorizza i metadati su un'azione ordinaria o ETF.

    Parameters
    ----------
    name : `str`
        Il nome dell'asset (ad es. il nome dell'azienda e/o
        la clase delle azioni).
    symbol : `str`
        Il simbolo ticker originale dell'asset
        TODO: modifiche per gestire la corretta mappatura dei ticker.
    tax_exempt: `boolean`, optional
        La quota è esente da tassazione governativa?
        Necessario per la tassazione sulle transazioni azionarie.
    """

    def __init__(
        self,
        name,
        symbol,
        tax_exempt=True
    ):
        self.cash_like = False
        self.name = name
        self.symbol = symbol
        self.tax_exempt = tax_exempt

    def __repr__(self):
        """
        Rappresentazione in stringa dell'Asset azionario.
        """
        return (
            "Equity(name='%s', symbol='%s', tax_exempt=%s)" % (
                self.name, self.symbol, self.tax_exempt
            )
        )
