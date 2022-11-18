from abc import ABCMeta, abstractmethod


class TradingSession(object):
    """
    Interfaccia a una sessione di trading live o backtesting.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self):
        raise NotImplementedError(
            "Should implement run()"
        )
