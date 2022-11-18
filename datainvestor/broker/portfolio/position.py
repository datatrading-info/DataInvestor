from math import floor

import numpy as np


class Position(object):
    """
    Gestisce la contabilizzazione dell'inserimento di una nuova
    posizione in un asset insieme alle successive modifiche
    tramite operazioni aggiuntive.

    L'approccio qui adottato separa il lato long e short a fini
    contabili. Include anche un profitto e una perdita correnti
    non realizzati e realizzati della posizione.

    Parameters
    ----------
    asset : `str`
        La stringa del simbolo dell'asset
    current_price : `float`
        Il prezzo iniziale della Posizione.
    current_dt : `pd.Timestamp`
        L'ora in cui è stata creata la posizione.
    buy_quantity : `int`
        L'importo del bene acquistato.
    sell_quantity : `int`
        L'importo del bene venduto.
    avg_bought : `float`
        Il prezzo iniziale pagato per comprare gli asset.
    avg_sold : `float`
        Il prezzo iniziale pagato per vendere gli asset.
    buy_commission : `float`
        La commisione spesa per comprare gli asset per questa posizione.
    sell_commission : `float`
        La commisione spesa per vendere gli asset per questa posizione
    """

    def __init__(
        self,
        asset,
        current_price,
        current_dt,
        buy_quantity,
        sell_quantity,
        avg_bought,
        avg_sold,
        buy_commission,
        sell_commission
    ):
        self.asset = asset
        self.current_price = current_price
        self.current_dt = current_dt
        self.buy_quantity = buy_quantity
        self.sell_quantity = sell_quantity
        self.avg_bought = avg_bought
        self.avg_sold = avg_sold
        self.buy_commission = buy_commission
        self.sell_commission = sell_commission

    @classmethod
    def open_from_transaction(cls, transaction):
        """
        Costruisce una nuova istanza di posizione dalla transazione fornita.

        Parameters
        ----------
        transaction : `Transaction`
            L'operazione con cui aprire la Posizione.

        Returns
        -------
        `Position`
            La posizione istanziata.
        """
        asset = transaction.asset
        current_price = transaction.price
        current_dt = transaction.dt

        if transaction.quantity > 0:
            buy_quantity = transaction.quantity
            sell_quantity = 0
            avg_bought = current_price
            avg_sold = 0.0
            buy_commission = transaction.commission
            sell_commission = 0.0
        else:
            buy_quantity = 0
            sell_quantity = -1.0 * transaction.quantity
            avg_bought = 0.0
            avg_sold = current_price
            buy_commission = 0.0
            sell_commission = transaction.commission

        return cls(
            asset,
            current_price,
            current_dt,
            buy_quantity,
            sell_quantity,
            avg_bought,
            avg_sold,
            buy_commission,
            sell_commission
        )

    def _check_set_dt(self, dt):
        """
        Verifica che il timestamp fornito sia valido e in tal caso
        imposta il nuovo orario corrente della Posizione.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp da controllare e potenzialmente utilizzare
            come nuova ora corrente.
        """
        if dt is not None:
            if (dt < self.current_dt):
                raise ValueError(
                    'Supplied update time of "%s" is earlier than '
                    'the current time of "%s".' % (dt, self.current_dt)
                )
            else:
                self.current_dt = dt

    @property
    def direction(self):
        """
        Restituisce un valore intero che rappresenta la direzione.

        Returns
        -------
        `int`
            1 - Long, 0 - No direction, -1 - Short.
        """
        if self.net_quantity == 0:
            return 0
        else:
            return np.copysign(1, self.net_quantity)

    @property
    def market_value(self):
        """
        Restituire il valore di mercato (rispettando la direzione) della
        Posizione in base al prezzo corrente disponibile per la Posizione.

        Returns
        -------
        `float`
            L'attuale valore di mercato della Posizione.
        """
        return self.current_price * self.net_quantity

    @property
    def avg_price(self):
        """
        Il prezzo medio pagato per tutte le attività sul lato long o short.

        Returns
        -------
        `float`
            Il prezzo medio sul lato lungo o corto.
        """
        if self.net_quantity == 0:
            return 0.0
        elif self.net_quantity > 0:
            return (self.avg_bought * self.buy_quantity + self.buy_commission) / self.buy_quantity
        else:
            return (self.avg_sold * self.sell_quantity - self.sell_commission) / self.sell_quantity

    @property
    def net_quantity(self):
        """
        La differenza nella quantità degli asset acquistati e venduti fino ad oggi.

        Returns
        -------
        `int`
            La quantità netta di asset.
        """
        return self.buy_quantity - self.sell_quantity

    @property
    def total_bought(self):
        """
        Calcola il costo medio totale degli asset acquistati.

        Returns
        -------
        `float`
            Il costo medio totale degli asset acquistati.
        """
        return self.avg_bought * self.buy_quantity

    @property
    def total_sold(self):
        """
        Calcola il costo medio totale degli asset venduti.

        Returns
        -------
        `float`
            Il costo medio totale degli asset vendute.
        """
        return self.avg_sold * self.sell_quantity

    @property
    def net_total(self):
        """
        Calcola il costo medio totale netto degli asset
        acquistati e venduti.

        Returns
        -------
        `float`
            Il costo medio totale netto degli asset acquistati e venduti.
        """
        return self.total_sold - self.total_bought

    @property
    def commission(self):
        """
        Calcola le commissioni totali degli asset acquistati e venduti.

        Returns
        -------
        `float`
            Il totale delle commissioni degli asset acquistati e venduti.
        """
        return self.buy_commission + self.sell_commission

    @property
    def net_incl_commission(self):
        """
        Calcola il costo medio totale netto degli asset acquistati e venduti
        inclusa la commissione.

        Returns
        -------
        `float`           
            Il costo medio totale netto degli asset acquistati e venduti
             inclusa la commissione.
        """
        return self.net_total - self.commission

    @property
    def realised_pnl(self):
        """
        Calcola l'utile e la perdita (P&L) che è stato "realizzato" tramite
        due transazioni opposte nella posizione fino ad oggi.

        Returns
        -------
        `float`
            Il P&L realizzato calcolato.
        """
        if self.direction == 1:
            if self.sell_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.sell_quantity) -
                    ((self.sell_quantity / self.buy_quantity) * self.buy_commission) -
                    self.sell_commission
                )
        elif self.direction == -1:
            if self.buy_quantity == 0:
                return 0.0
            else:
                return (
                    ((self.avg_sold - self.avg_bought) * self.buy_quantity) -
                    ((self.buy_quantity / self.sell_quantity) * self.sell_commission) -
                    self.buy_commission
                )
        else:
            return self.net_incl_commission

    @property
    def unrealised_pnl(self):
        """
        Calcola il profitto e la perdita (P&L) che deve ancora essere
        "realizzato" nella rimanente quantità di asset diversa
        da zero, a causa del prezzo di mercato corrente.

        Returns
        -------
        `float`
            The calculated unrealised P&L.
        """
        return (self.current_price - self.avg_price) * self.net_quantity

    @property
    def total_pnl(self):
        """
        Calcola la somma degli utili e delle perdite (P&L) non realizzati e realizzati.

        Returns
        -------
        `float`
           La somma dei profitti e delle perdite non realizzati e realizzati.
        """
        return self.realised_pnl + self.unrealised_pnl

    def update_current_price(self, market_price, dt=None):
        """
        Aggiorna lo stato della Posizione con l'attuale prezzo di mercato
        dell'Asset, ad uno specifico timestamp opzionale.

        Parameters
        ----------
        market_price : `float`
            l'attuale prezzo di mercato
        dt : `pd.Timestamp`, optional
            La data e ora dell'attuale prezzo di mercato (opzionale).
        """
        self._check_set_dt(dt)

        if market_price <= 0.0:
            raise ValueError(
                'Market price "%s" of asset "%s" must be positive to '
                'update the position.' % (market_price, self.asset)
            )
        else:
            self.current_price = market_price

    def _transact_buy(self, quantity, price, commission):
        """
        Gestione della contabilità per creare una nuova gamba
        long per la Posizione.

        Parameters
        ----------
        quantity : `int`
            La quantità aggiuntiva di asset da acquistare.
        price : `float`
            Il prezzo a cui è stata acquistata questa gamba.
        commission : `float`
            La commissione pagata al broker per l'acquisto.
        """
        self.avg_bought = ((self.avg_bought * self.buy_quantity) + (quantity * price)) / (self.buy_quantity + quantity)
        self.buy_quantity += quantity
        self.buy_commission += commission

    def _transact_sell(self, quantity, price, commission):
        """
        Gestione della contabilità per creare una nuova gamba
        short per la Posizione.

        Parameters
        ----------
        quantity : `int`
            La quantità aggiuntiva di asset da vendere.
        price : `float`
            Il prezzo a cui è stata venduta questa gamba.
        commission : `float`
            La commissione pagata al broker per la vendita.
        """
        self.avg_sold = ((self.avg_sold * self.sell_quantity) + (quantity * price)) / (self.sell_quantity + quantity)
        self.sell_quantity += quantity
        self.sell_commission += commission

    def transact(self, transaction):
        """
        Calcola gli aggiustamenti alla Posizione che si verificano
        quando vengono acquistate e vendute nuove unità in un Asset.

        Parameters
        ----------
        transaction : `Transaction`
            L'Operazione con cui aggiornare la Posizione.
        """
        if self.asset != transaction.asset:
            raise ValueError(
                'Failed to update Position with asset %s when '
                'carrying out transaction in asset %s. ' % (
                    self.asset, transaction.asset
                )
            )

        # Niente da fare se la transazione non ha quantità
        if int(floor(transaction.quantity)) == 0:
            return

        # A seconda della direzione della transazione,
        # assicurarsi che venga chiamato il calcolo corretto
        if transaction.quantity > 0:
            self._transact_buy(
                transaction.quantity,
                transaction.price,
                transaction.commission
            )
        else:
            self._transact_sell(
                -1.0 * transaction.quantity,
                transaction.price,
                transaction.commission
            )

        # Aggiorna le attuali informazioni del trade
        self.update_current_price(transaction.price, transaction.dt)
        self.current_dt = transaction.dt
