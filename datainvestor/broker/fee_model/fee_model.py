from abc import ABCMeta, abstractmethod


class FeeModel(object):
    """
    Classe astratta per gestire il calcolo delle
    commissioni del broker e delle tasse.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def _calc_commission(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_commission()"
        )

    @abstractmethod
    def _calc_tax(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement _calc_tax()"
        )

    @abstractmethod
    def calc_total_cost(self, asset, quantity, consideration, broker=None):
        raise NotImplementedError(
            "Should implement calc_total_cost()"
        )
