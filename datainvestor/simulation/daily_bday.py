import datetime

import pandas as pd
from pandas.tseries.offsets import BDay
import pytz

from datainvestor.simulation.sim_engine import SimulationEngine
from datainvestor.simulation.event import SimulationEvent


class DailyBusinessDaySimulationEngine(SimulationEngine):
    """
    Una sottoclasse di SimulationEngine che genera eventi con una
    frequenza giornaliera predefinita per i tipici giorni lavorativi,
    ovvero dal lunedì al venerdì.

    In particolare, non tiene conto di eventuali festività regionali
    specifiche, come le festività nazionali.

    Produce un evento pre-mercato, un evento di mercato aperto, un
    evento di chiusura del mercato e un evento post-mercato per tutti
    i giorni tra la data di inizio e di fine.

    Parameters
    ----------
    starting_day : `pd.Timestamp`
        Il giorno di inizio della simulazione.
    ending_day : `pd.Timestamp`
        Il giorno finale della simulazione.
    pre_market : `Boolean`, optional
        Se includere un evento pre-mercato.
    post_market : `Boolean`, optional
        Se includere un evento post-mercato.
    """

    def __init__(self, starting_day, ending_day, pre_market=True, post_market=True):
        if ending_day < starting_day:
            raise ValueError(
                "Ending date time %s is earlier than starting date time %s. "
                "Cannot create DailyBusinessDaySimulationEngine "
                "instance." % (ending_day, starting_day)
            )

        self.starting_day = starting_day
        self.ending_day = ending_day
        self.pre_market = pre_market
        self.post_market = post_market
        self.business_days = self._generate_business_days()

    def _generate_business_days(self):
        """
        Genera l'elenco dei giorni lavorativi utilizzando la
        mezzanotte UTC come timestamp.

        Returns
        -------
        `list[pd.Timestamp]`
            L'elenco dell'intervallo di giorni lavorativi.
        """
        days = pd.date_range(
            self.starting_day, self.ending_day, freq=BDay()
        )
        return days

    def __iter__(self):
        """
        Genera i timestamp giornalieri e le informazioni sugli eventi
        per il pre-mercato, l'apertura del mercato, la chiusura del
        mercato e il post-mercato.

        Yields
        ------
        `SimulationEvent`
            Evento di simulazione del tempo di mercato per la resa
        """
        for index, bday in enumerate(self.business_days):
            year = bday.year
            month = bday.month
            day = bday.day

            if self.pre_market:
                yield SimulationEvent(
                    pd.Timestamp(
                        datetime.datetime(year, month, day), tz='UTC'
                    ), event_type="pre_market"
                )

            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day, 14, 30),
                    tz=pytz.utc
                ), event_type="market_open"
            )

            yield SimulationEvent(
                pd.Timestamp(
                    datetime.datetime(year, month, day, 21, 00),
                    tz=pytz.utc
                ), event_type="market_close"
            )

            if self.post_market:
                yield SimulationEvent(
                    pd.Timestamp(
                        datetime.datetime(year, month, day, 23, 59), tz='UTC'
                    ), event_type="post_market"
                )
