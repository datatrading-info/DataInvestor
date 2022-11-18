import pandas as pd
import pytz

from datainvestor.system.rebalance.rebalance import Rebalance


class WeeklyRebalance(Rebalance):
    """
    Genera un elenco di timestamp di ribilanciamento per pre o post-mercato,
    per un particolare giorno di negoziazione della settimana compreso
    tra le date di inizio e di fine fornite.

    Tutti i timestamp prodotti sono impostati su UTC.

    Parameters
    ----------
    start_date : `pd.Timestamp`
        Il timestamp di inizio dell'intervallo di ribilanciamento.
    end_date : `pd.Timestamp`
        Il timestamp finale dell'intervallo di ribilanciamento.
    weekday : `str`
        La rappresentazione in stringa di tre lettere del giorno della
        settimana su cui ribilanciare una volta alla settimana.
    pre_market : `Boolean`, optional
        Se effettuare il ribilanciamento ad apertura/chiusura del mercato.
    """

    def __init__(
        self,
        start_date,
        end_date,
        weekday,
        pre_market=False
    ):
        self.weekday = self._set_weekday(weekday)
        self.start_date = start_date
        self.end_date = end_date
        self.pre_market_time = self._set_market_time(pre_market)
        self.rebalances = self._generate_rebalances()

    def _set_weekday(self, weekday):
        """
        Verifica che la stringa del giorno della settimana
        corrisponda a un giorno della settimana lavorativo.

        Parameters
        ----------
        weekday : `str`
            La rappresentazione in stringa di tre lettere del giorno
            della settimana su cui ribilanciare una volta alla settimana.

        Returns
        -------
        `str`
            La rappresentazione di stringa di tre lettere maiuscole del giorno
            della settimana su cui ribilanciare una volta alla settimana.
        """
        weekdays = ("MON", "TUE", "WED", "THU", "FRI")
        if weekday.upper() not in weekdays:
            raise ValueError(
                "Provided weekday keyword '%s' is not recognised "
                "or not a valid weekday." % weekday
            )
        else:
            return weekday.upper()

    def _set_market_time(self, pre_market):
        """
        Determina se utilizzare l'apertura o la chiusura del
        mercato come tempo di ribilanciamento.

        Parameters
        ----------
        pre_market : `Boolean`
            se utilizzare l'apertura o la chiusura del
            mercato come tempo di ribilanciamento.

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
        rebalance_dates = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='W-%s' % self.weekday
        )

        rebalance_times = [
            pd.Timestamp(
                "%s %s" % (date, self.pre_market_time), tz=pytz.utc
            )
            for date in rebalance_dates
        ]

        return rebalance_times
