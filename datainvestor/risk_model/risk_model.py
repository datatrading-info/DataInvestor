from abc import ABCMeta, abstractmethod


class RiskModel(object):
    """
    Interfaccia astratta per un RiskModel.

    Un'istanza di classe derivata di RiskModel accetta un Asset Universe
    e un'istanza DataHandler opzionale per modificare i pesi sugli Asset
    generati da un AlphaModel.

    Questi pesi rettificati vengono usati del PortfolioConstructionModel
    per generare nuovi pesi target per il portafoglio.

    L'implementazione di __call__ produce un dizionario con chiave Asset
    e con un valore scalare come segnale.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt, weights):
        raise NotImplementedError(
            "Should implement __call__()"
        )
