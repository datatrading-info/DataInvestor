import numpy as np

from datainvestor.portcon.order_sizer.order_sizer import OrderSizer


class LongShortLeveragedOrderSizer(OrderSizer):
    """
    Creates a target portfolio of quantities for each Asset
    using its provided weight and total equity available in the
    Broker portfolio, leveraging up if necessary via the supplied
    gross leverage.

    Crea un portafoglio target con le quantità per ogni asset utilizzando
    il peso fornito e il capitale totale disponibile nel portafoglio del
    broker, sfruttando se necessario la leva lorda fornita.

    Parameters
    ----------
    broker : `Broker`
        L'istanza Broker derivata da cui ottenere l'equità del portafoglio.
    broker_portfolio_id : `str`
        Il portafoglio specifico presso il Broker da cui ottenere capitale.
    data_handler : `DataHandler`
        Da cui ottenere gli ultimi prezzi degli asset.
    gross_leverage : `float`, optional
        La quantità di leva percentuale da utilizzare per il
        dimensionamento degli ordini.
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        data_handler,
        gross_leverage=1.0
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.gross_leverage = self._check_set_gross_leverage(
            gross_leverage
        )

    def _check_set_gross_leverage(self, gross_leverage):
        """
        Verifica e imposta il valore percentuale della leva finanziaria lorda.

        Parameters
        ----------
        gross_leverage : `float`
            La quantità di leva percentuale da utilizzare per il dimensionamento
            degli ordini. Ciò presuppone nessuna restrizione sul margine.

        Returns
        -------
        `float`
            Il valore percentuale della leva finanziaria lorda.
        """
        if (
            gross_leverage <= 0.0
        ):
            raise ValueError(
                'Gross leverage "%s" provided to long-short levered '
                'order sizer is non positive.' % gross_leverage
            )
        else:
            return gross_leverage

    def _obtain_broker_portfolio_total_equity(self):
        """
        Calcola il capitale totale del portafoglio Broker.

        Returns
        -------
        `float`
            Il patrimonio totale del portafoglio Broker.
        """
        return self.broker.get_portfolio_total_equity(self.broker_portfolio_id)

    def _normalise_weights(self, weights):
        """
        Riscala i valori dei pesie forniti per garantire che
        i pesi siano ridimensionati in base all'esposizione
        lorda divisa per la leva finanziaria lorda.

        Parameters
        ----------
        weights : `dict{Asset: float}`
            Il vettore dei pesi non normalizzati.

        Returns
        -------
        `dict{Asset: float}`
            Il vettore dei pesi non normalizzati.
        """
        gross_exposure = sum(np.abs(weight) for weight in weights.values())

        # Se i pesi sono molto vicini o uguali a zero, il ridimensionamento
        # non è possibile, quindi restituisce i pesi non ridimensionati
        if np.isclose(gross_exposure, 0.0):
            return weights

        gross_ratio = self.gross_leverage / gross_exposure

        return {
            asset: (weight * gross_ratio)
            for asset, weight in weights.items()
        }

    def __call__(self, dt, weights):
        """
        Crea un portafoglio target long short con leva dai pesi
        target forniti in un determinato timestamp.

        Parameters
        ----------
        dt : `pd.Timestamp`
            La data e l'ora corrente.
        weights : `dict{Asset: float}`
            I pesi target (potenzialmente non normalizzati).

        Returns
        -------
        `dict{Asset: dict}`
            Il dizionario delle quantità dei target long short target del portfolio.
        """
        total_equity = self._obtain_broker_portfolio_total_equity()

        # Pesi inziali
        N = len(weights)
        if N == 0:
            # Nessuna previsione quindi il portafoglio rimane
            # in contanti o è completamente liquidato
            return {}

        # Scala i pesi per tenere conto dell'esposizione lorda e della leva finanziaria
        normalised_weights = self._normalise_weights(weights)

        target_portfolio = {}
        for asset, weight in sorted(normalised_weights.items()):
            pre_cost_dollar_weight = total_equity * weight

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

            # Tronca al numero intero più vicino il peso
            # dopo costo del dollaro
            truncated_after_cost_dollar_weight = (
                np.floor(after_cost_dollar_weight)
                if after_cost_dollar_weight >= 0.0
                else np.ceil(after_cost_dollar_weight)
            )
            asset_quantity = int(
                truncated_after_cost_dollar_weight / asset_price
            )

            # Aggiunto al portafoglio target
            target_portfolio[asset] = {"quantity": asset_quantity}

        return target_portfolio
