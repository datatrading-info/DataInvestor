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
        self.rebalances = [start_dt]
