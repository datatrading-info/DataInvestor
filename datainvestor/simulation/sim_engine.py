from abc import ABCMeta, abstractmethod


class SimulationEngine(object):
    """
    Interfaccia per un motore di simulazione di eventi di trading.

    Le sottoclassi sono progettate per prendere i timestamp di inizio
    e fine per generare eventi a una frequenza specifica.

    Ciò si ottiene sovrascrivendo __iter__ e restituendo entità Event.
    Queste entità includerebbero la segnalazione di un'apertura di borsa,
    una chiusura di borsa, nonché eventi pre e post-apertura per consentire
    la gestione dei flussi di cassa e delle azioni societarie.

    In questo modo possono essere eseguiti gli eventi necessari per le entità
    nel sistema, come la gestione dei dividendi, le variazioni di capitale,
    il calcolo della performance e gli ordini di negoziazione.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError(
            "Should implement __iter__()"
        )
