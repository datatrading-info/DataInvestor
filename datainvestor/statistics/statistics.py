from abc import ABCMeta, abstractmethod


class Statistics(object):
    """
    Statistics è una classe astratta che fornisce un'interfaccia per tutte
    le classi statistiche ereditate (live, storiche, personalizzate, ecc.).

    L'obiettivo di un oggetto Statistics è mantenere un registro delle informazioni
    utili su una o più strategie di trading mentre la strategia è in esecuzione.
    Ciò avviene collegandosi al ciclo dell'evento principale ed essenzialmente
    aggiornando l'oggetto in base alle prestazioni del portafoglio nel tempo.

    Idealmente, le statistiche dovrebbero essere sottoclassificate in base alle
    strategie e ai timeframe tradati dall'utente. Strategie di trading diverse
    possono richiedere l'aggiornamento di metriche o frequenze di metriche diverse,
    tuttavia l'esempio fornito è adatto per timeframe più lunghi.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, dt):
        """
        Aggiorna tutte le statistiche in base ai valori del portafoglio
        e delle posizioni aperte. Questo dovrebbe essere chiamato
        dall'interno del ciclo di eventi.
        """
        raise NotImplementedError("Should implement update()")

    @abstractmethod
    def get_results(self):
        """
        Restituisce un dict contenente tutte le statistiche.
        """
        raise NotImplementedError("Should implement get_results()")

    @abstractmethod
    def plot_results(self):
        """
        Grafico di tutte le statistiche raccolte fino ad 'ora'
        """
        raise NotImplementedError("Should implement plot_results()")

    @abstractmethod
    def save(self, filename):
        """
        Salva i risultati delle statistiche in un file
        """
        raise NotImplementedError("Should implement save()")
