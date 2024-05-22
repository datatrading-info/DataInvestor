import pandas as pd
from pandas.tseries.offsets import BusinessDay
from datainvestor.system.rebalance.rebalance import Rebalance


class BuyAndHoldRebalance(Rebalance):
    """
    Genera un unico timestamp di ribilanciamento alla data di inizio
    per creare un unico insieme di ordini all'inizio di un backtest,
    senza ulteriori ribilanciamenti effettuati.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e l'ora di inizio del ribilanciamento di buy and hold.
    """

    def __init__(self, start_dt):
        self.start_dt = start_dt
        self.rebalances = self._generate_rebalances()

    def _is_business_day(self):
        """
        Controllo se start_dt è un giorno lavorativo

        Returns
        -------
        `boolean`
        """
        return bool(len(pd.bdate_range(self.start_dt, self.start_dt)))

    def _generate_rebalances(self):
        """
        Restituisce il timestamp del prossimo giorno lavorativo per fare il ribilanciamento.

        Non include le festività.

        Returns
        -------
        `list[pd.Timestamp]`
            Lista di timestamp di ribilancamento
        """
        if not self._is_business_day():
            rebalance_date = self.start_dt + BusinessDay()
        else:
            rebalance_date = self.start_dt
        return [rebalance_date]