from datainvestor.broker.fee_model.fee_model import FeeModel


class PercentFeeModel(FeeModel):
    """
    Una sottoclasse FeeModel che produce un costo percentuale
    per tasse e commissioni.

    Parameters
    ----------
    commission_pct : `float`, optional
        La commissione percentuale applicata al corrispettivo.
        0-100% è nell'intervallo [0,0, 1,0]. Quindi, ad es. 0,1% è 0,001
    tax_pct : `float`, optional
        L'imposta percentuale applicata al corrispettivo.
        0-100% è nell'intervallo [0,0, 1,0]. Quindi, ad es. 0,1% è 0,001
    """

    def __init__(self, commission_pct=0.0, tax_pct=0.0):
        super().__init__()
        self.commission_pct = commission_pct
        self.tax_pct = tax_pct

    def _calc_commission(self, asset, quantity, consideration, broker=None):
        """
        Restituisce la commissione percentuale dal corrispettivo.

        Parameters
        ----------
        asset : `str`
            Stringa del simbolo dell'asset.
        quantity : `int`
            La quantità di asset (necessaria per i calcoli
            in stile InteractiveBrokers).
        consideration : `float`
            Prezzo moltiplicato per quantità dell'ordine.
        broker : `Broker`, optional
            Riferimento ad un broker (opzionale).

        Returns
        -------
        `float`
            La percentuale di commssione.
        """
        return self.commission_pct * abs(consideration)

    def _calc_tax(self, asset, quantity, consideration, broker=None):
        """
        Restituisce la tassa percentuale dal corrispettivo.

        Parameters
        ----------
        asset : `str`
            Stringa del simbolo dell'asset.
        quantity : `int`
            La quantità di asset (necessaria per i calcoli
            in stile InteractiveBrokers).
        consideration : `float`
            Prezzo moltiplicato per quantità dell'ordine.
        broker : `Broker`, optional
            Riferimento ad un broker (opzionale).

        Returns
        -------
        `float`
            La percentuale di tasse.
        """
        return self.tax_pct * abs(consideration)

    def calc_total_cost(self, asset, quantity, consideration, broker=None):
        """
        Calcola il totale di qualsiasi commissione e/o tassa
        per il trade della dimensione 'corrispettiva'.

        Parameters
        ----------
        asset : `str`
            Stringa del simbolo dell'asset.
        quantity : `int`
            La quantità di asset (necessaria per i calcoli
            in stile InteractiveBrokers).
        consideration : `float`
            Prezzo moltiplicato per quantità dell'ordine.
        broker : `Broker`, optional
            Riferimento ad un broker (opzionale).

        Returns
        -------
        `float`
            Totale di commissioni e tasse.
        """
        commission = self._calc_commission(asset, quantity, consideration, broker)
        tax = self._calc_tax(asset, quantity, consideration, broker)
        return commission + tax
