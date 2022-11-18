from abc import ABCMeta, abstractmethod


class AlphaModel(object):
    """
    Interfaccia astratta per un richiamabile AlphaModel.

    Un'istanza di classe derivata di AlphaModel accetta un asset
    Universe e un'istanza DataHandler (opzionale) in modo
    per generare segnali di previsione sugli Asset.

    Questi segnali sono utilizzati dal PortfolioConstructionModel
    per generare pesi target per il portafoglio.

    L'implementazione di __call__ produce un dizionario digitato da
    Asset e con un valore scalare come segnale.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt):
        raise NotImplementedError(
            "Should implement __call__()"
        )
