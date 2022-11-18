from abc import ABCMeta, abstractmethod


class OrderSizer(object):
    """
    Crea un portafoglio target di quantità per ciascun Asset utilizzando
    il peso fornito e il capitale totale disponibile nel portafoglio Broker.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, dt, weights):
        raise NotImplementedError(
            "Should implement call()"
        )
