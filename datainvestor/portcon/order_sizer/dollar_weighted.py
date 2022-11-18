import numpy as np

from datainvestor.portcon.order_sizer.order_sizer import OrderSizer


class DollarWeightedCashBufferedOrderSizer(OrderSizer):
    """
    Crea un portafoglio target di quantità per ciascun asset
    utilizzando il peso fornito e il capitale totale disponibile
    nel portafoglio Broker.

    Include un opzione buffer di liquidità a causa dell'importo non
    frazionario delle dimensioni delle azioni/unità. Il buffer di liquidità
    è predefinito al 5% del capitale totale, ma può essere modificato.

    Parameters
    ----------
    broker : `Broker`
        L'istanza Broker derivata da cui ottenere il capitale del portafoglio.
    broker_portfolio_id : `str`
        Il portafoglio specifico presso il Broker da cui ottenere capitale.
    data_handler : `DataHandler`
        Per ottenere gli ultimi prezzi degli asset
    cash_buffer_percentage : `float`, optional
        La percentuale del capitale del portafoglio da trattenere in contanti
        per evitare di generare ordini che superano il capitale del conto
        (supponendo che non vi sia alcun margine disponibile).
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        data_handler,
        cash_buffer_percentage=0.05
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.cash_buffer_percentage = self._check_set_cash_buffer(
            cash_buffer_percentage
        )

    def _check_set_cash_buffer(self, cash_buffer_percentage):
        """
        Verifica e imposta il valore percentuale del buffer di liquidità.

        Parameters
        ----------
        cash_buffer_percentage : `float`
            The percentage of the portfolio equity to retain in
            cash to avoid generating Orders that exceed account
            equity (assuming no margin available).
            La percentuale del capitale del portafoglio da trattenere in
            contanti per evitare di generare ordini che superano il capitale
            del conto (supponendo che non vi sia margine disponibile).

        Returns
        -------
        `float`
            Il valore percentuale del buffer di liquidità.
        """
        if (
            cash_buffer_percentage < 0.0 or cash_buffer_percentage > 1.0
        ):
            raise ValueError(
                'Cash buffer percentage "%s" provided to dollar-weighted '
                'execution algorithm is negative or '
                'exceeds 100%.' % cash_buffer_percentage
            )
        else:
            return cash_buffer_percentage

    def _obtain_broker_portfolio_total_equity(self):
        """
        Ricava l'equity totale del portafoglio Broker.

        Returns
        -------
        `float`
            Il patrimonio totale del portafoglio Broker.
        """
        return self.broker.get_portfolio_total_equity(self.broker_portfolio_id)

    def _normalise_weights(self, weights):
        """
        Riscala i valori di peso forniti per garantire
        che le somme dei pesi siano unitarie

        Parameters
        ----------
        weights : `dict{Asset: float}`
            Il vettore dei peso non normalizzati.

        Returns
        -------
        `dict{Asset: float}`
            Il vettore della somma unitaria dei pesi
        """
        if any([weight < 0.0 for weight in weights.values()]):
            raise ValueError(
                'Dollar-weighted cash-buffered order sizing does not support '
                'negative weights. All positions must be long-only.'
            )

        weight_sum = sum(weight for weight in weights.values())

        # Se i pesi sono molto vicini o uguali a zero, il ridimensionamento non
        # è possibile, quindi restituisce semplicemente i pesi non ridimensionati
        if np.isclose(weight_sum, 0.0):
            return weights

        return {
            asset: (weight / weight_sum)
            for asset, weight in weights.items()
        }

    def __call__(self, dt, weights):
        """
        Crea un portafoglio target con buffer di liquidità pesato in dollari
        a partire dai pesi target forniti in un determinato timestamp.

        Parameters
        ----------
        dt : `pd.Timestamp`
            La data e l'ora corrente.
        weights : `dict{Asset: float}`
            I pesi target (potenzialmente non normalizzati).

        Returns
        -------
        `dict{Asset: dict}`
            Il dizionario con le quantità del portafoglio target con
            buffer di liquidità.
        """
        total_equity = self._obtain_broker_portfolio_total_equity()
        cash_buffered_total_equity = total_equity * (
            1.0 - self.cash_buffer_percentage
        )

        # Pesi inziali
        N = len(weights)
        if N == 0:
            # Nessuna previsione quindi il portafoglio rimane
            # in contanti o è completamente liquidato
            return {}

        # Assicura che le somme dei vettori dei peso siano unitari
        normalised_weights = self._normalise_weights(weights)

        target_portfolio = {}
        for asset, weight in sorted(normalised_weights.items()):
            pre_cost_dollar_weight = cash_buffered_total_equity * weight

            # Stima le commissioni del broker per questo asset
            est_quantity = 0  # TODO: Bisogna aggiungere per IB
            est_costs = self.broker.fee_model.calc_total_cost(
                asset, est_quantity, pre_cost_dollar_weight, broker=self.broker
            )

            # Calcola la quantità di asset target integrale assumendo i costi del broker
            after_cost_dollar_weight = pre_cost_dollar_weight - est_costs
            asset_price = self.data_handler.get_asset_latest_ask_price(
                dt, asset
            )

            if np.isnan(asset_price):
                raise ValueError(
                    'Asset price for "%s" at timestamp "%s" is Not-a-Number (NaN). '
                    'This can occur if the chosen backtest start date is earlier '
                    'than the first available price for a particular asset. Try '
                    'modifying the backtest start date and re-running.' % (asset, dt)
                )

            # TODO: Solo Long in questo momento
            asset_quantity = int(
                np.floor(after_cost_dollar_weight / asset_price)
            )

            # Aggiunto al portafoglio target
            target_portfolio[asset] = {"quantity": asset_quantity}

        return target_portfolio
