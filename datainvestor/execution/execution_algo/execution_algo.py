from abc import ABCMeta, abstractmethod


class ExecutionAlgorithm(object):
    """
    Callable which takes in a list of desired rebalance Orders
    and outputs a new Order list with a particular execution
    algorithm strategy.

    Accetta un elenco di ordini di ribilanciamento desiderati e
    genera un nuovo elenco di ordini con una particolare
    strategia per l'algoritmo di esecuzione.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt, initial_orders):
        raise NotImplementedError(
            "Should implement __call__()"
        )
