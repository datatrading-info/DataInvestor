import numpy as np


class Transaction(object):
    """
    Gestisce la transazione di un bene, come utilizzato nella classe Posizione.

    Parameters
    ----------
    asset : `str`
        Il simbolo dell'asset della transazione
    quantity : `int`
        Numero intero di azioni nella transazione
    dt : `pd.Timestamp`
        Data e ora della transazione
    price : `float`
        Il prezzo della transazione effettuata
    order_id : `int`
        L'identificatore univoco dell'ordine
    commission : `float`, optional
        La comissione di trading
    """

    def __init__(
        self,
        asset,
        quantity,
        dt,
        price,
        order_id,
        commission=0.0
    ):
        self.asset = asset
        self.quantity = quantity
        self.direction = np.copysign(1, self.quantity)
        self.dt = dt
        self.price = price
        self.order_id = order_id
        self.commission = commission

    def __repr__(self):
        """
        Fornisce una rappresentazione della Transazione per consentire la ricreazione completa dell'oggetto.

        Returns
        -------
        `str`
            La rappresentazione in stringa della Transazione.
        """
        return "%s(asset=%s, quantity=%s, dt=%s, " \
            "price=%s, order_id=%s)" % (
                type(self).__name__, self.asset,
                self.quantity, self.dt,
                self.price, self.order_id
            )

    @property
    def cost_without_commission(self):
        """
        Calcola il costo della transazione senza includere
        eventuali costi di commissione.

        Returns
        -------
        `float`
            Il costo della transazione senza commissioni.
        """
        return self.quantity * self.price

    @property
    def cost_with_commission(self):
        """
        Calcola il costo della transazione incluso i costi di commissione.

        Returns
        -------
        `float`
            Il costo della transazione con le commissioni.
        """
        if self.commission == 0.0:
            return self.cost_without_commission
        else:
            return self.cost_without_commission + self.commission
