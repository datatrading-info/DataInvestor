from abc import ABCMeta, abstractmethod


class Rebalance(object):
    """
    Interfaccia a un elenco generico di logica di sistema
    e timestamp di ribilanciamento degli ordini di trading.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def output_rebalances(self):
        raise NotImplementedError(
            "Should implement output_rebalances()"
        )
