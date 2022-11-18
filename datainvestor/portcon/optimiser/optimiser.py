from abc import ABCMeta, abstractmethod


class PortfolioOptimiser(object):
    """
    Interfaccia astratta di un PortfolioOptimiser.

    Un'istanza di classe derivata di PortfolioOptimiser prende un
    elenco di asset (non un universo di asset) e un'istanza di
    DataHandler opzionale per generare i pesi target per gli asset.

    Questi sono poi potenzialmente modificati dal PortfolioConstructionModel,
    che genera un elenco di Ordini di ribilanciamento.

    L'implementazione di __call__ produce un dizionario con chiave Asset e
    con un valore scalare come peso.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt):
        raise NotImplementedError(
            "Should implement __call__()"
        )
