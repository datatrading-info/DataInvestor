import pandas as pd
import pytz

from datainvestor.system.rebalance.rebalance import Rebalance


class DailyRebalance(Rebalance):
    """
    Genera un elenco di timestamp di ribilanciamento per il pre o post-market,
    per tutti i giorni lavorativi (lunedì-venerdì) tra due date.

    Non tiene conto dei calendari delle festività.

    Tutti i timestamp prodotti sono impostati su UTC.

    Parameters
    ----------
    start_date : `pd.Timestamp`
        Il timestamp di inizio dell'intervallo di ribilanciamento.
    end_date : `pd.Timestamp`
        Il timestamp finale dell'intervallo di ribilanciamento
    pre_market : `Boolean`, optional
        Se effettuare il ribilanciamento ad apertura/chiusura del mercato.
    """

    def __init__(
        self,
        start_date,
        end_date,
        pre_market=False
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_market_time(self, pre_market):
        """
        Determina se utilizzare l'apertura del mercato o la chiusura
        del mercato per il ribilanciamento.

        Parameters
        ----------
        pre_market : `Boolean`
            se utilizzare l'apertura del mercato o la chiusura
            del mercato per il ribilanciamento.

        Returns
        -------
        `str`
            La rappresentazione in stringa dell'orario di ribilanciamento.
        """
        return "14:30:00" if pre_market else "21:00:00"

    def _generate_rebalances(self):
        """
        Restituisce l'elenco dei timestamp di ribilanciamento.

        Returns
        -------
        `list[pd.Timestamp]`
            L'elenco dei timestamp di ribilanciamento.
        """
        rebalance_dates = pd.bdate_range(
            start=self.start_date, end=self.end_date,
        )

        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.market_time), tz=pytz.utc
            )
            for date in rebalance_dates
        ]

        return rebalance_times
