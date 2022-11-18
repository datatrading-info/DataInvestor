import datetime

from datainvestor.exchange.exchange import Exchange


class SimulatedExchange(Exchange):
    """
    La classe SimulatedExchange viene utilizzata per modellare
    una sede di negoziazione dal vivo.

    Espone i metodi per informare un'istanza della classe client
    quando l'exchange scambio è aperto per determinare quando
    gli ordini possono essere eseguiti.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        il timestamp di inizio dell'exchange simulato.
    """

    def __init__(self, start_dt):
        self.start_dt = start_dt

        # TODO: Eliminare hardcoding di NYSE
        # TODO: Gestire il fuso orario
        self.open_dt = datetime.time(14, 30)
        self.close_dt = datetime.time(21, 00)

    def is_open_at_datetime(self, dt):
        """
        Questa logica è semplicistica in quanto controlla solo
        se il timestamp fornito è compreso tra le ore di mercato
        aperto in un giorno feriale.

        Non esiste una gestione storica del calendario o un concetto
        di giorni di festività per l'exchange.

        Parameters
        ----------
        dt : `pd.Timestamp`
            timestamp da verificare gli orari di mercato aperto.

        Returns
        -------
        `Boolean`
            Se l'exchange aperto in questo timestamp.
        """
        if dt.weekday() > 4:
            return False
        return self.open_dt <= dt.time() and dt.time() < self.close_dt
