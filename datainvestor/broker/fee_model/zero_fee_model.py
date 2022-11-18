from datainvestor.broker.fee_model.fee_model import FeeModel


class ZeroFeeModel(FeeModel):
    """
    Una sottoclasse di FeeModel che produce nessuna commisione o
    tasse. Questo è il modello default delle commission per
    simulare il brokerages con datainvestor.
    """

    def _calc_commission(self, asset, quantity, consideration, broker=None):
        """
        Returns zero commission.

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
            Le commissione a costo zero.
        """
        return 0.0

    def _calc_tax(self, asset, quantity, consideration, broker=None):
        """
        Restituisce le tasse a zero.

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
            Le tasse a costo zero.
        """
        return 0.0

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
            Totale delle commission e tasse a costo zero.
        """
        commission = self._calc_commission(asset, quantity, consideration, broker)
        tax = self._calc_tax(asset, quantity, consideration, broker)
        return commission + tax
