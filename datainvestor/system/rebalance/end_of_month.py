import pandas as pd
import pytz

from datainvestor.system.rebalance.rebalance import Rebalance


class EndOfMonthRebalance(Rebalance):
    """
    Genera un elenco di timestamp di ribilanciamento per il pre o post-market,
    per l'ultimo giorno di calendario del mese compreso tra le date di
    inizio e fine fornite.

    Tutti i timestamp prodotti sono impostati su UTC.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e l'ora di inizio dell'intervallo di ribilanciamento.
    end_dt : `pd.Timestamp`
        La data e l'ora di fine dell'intervallo di ribilanciamento.
    pre_market : `Boolean`, optional
        Se effettuare il ribilanciamento all'apertura/chiusura del mercato
        nell'ultimo giorno del mese. Il valore predefinito è False,
        ovvero alla chiusura del mercato.
    """

    def __init__(
        self,
        start_dt,
        end_dt,
        pre_market=False
    ):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_market_time(self, pre_market):
        """
        Determina se utilizzare mercato aperto o mercato chiuso
        come tempo di ribilanciamento.

        Parameters
        ----------
        pre_market : `Boolean`
            Se il ribilanciamento viene effettuato ad apertura/chiusura del mercato.

        Returns
        -------
        `str`
            La stringa di tempo utilizzata per la costruzione del timestamp di Pandas.
        """
        return "14:30:00" if pre_market else "21:00:00"

    def _generate_rebalances(self):
        """
        Utilizza il metodo Pandas date_range per creare l'elenco
        appropriato di timestamp di ribilanciamento.

        Returns
        -------
        `List[pd.Timestamp]`
            L'elenco dei timestamp di ribilanciamento.
        """
        rebalance_dates = pd.date_range(
            start=self.start_dt,
            end=self.end_dt,
            freq='BM'
        )

        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.market_time), tz=pytz.utc
            )
            for date in rebalance_dates
        ]
        return rebalance_times
