from abc import ABCMeta, abstractmethod


class Exchange(object):
    """
    Interface to a trading exchange such as the NYSE or LSE.
    This class family is only required for simulations, rather than
    live or paper trading.

    It exposes methods for obtaining calendar capability
    for trading opening times and market events.

    Interfaccia a una borsa di scambio come NYSE o LSE.
    Questa famiglia di classi è richiesta solo per le simulazioni,
    invece che per il live o paper trading.

    Espone i metodi per ottenere il calendario per gli orari di
    apertura del trading e gli eventi di mercato.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def is_open_at_datetime(self, dt):
        raise NotImplementedError(
            "Should implement is_open_at_datetime()"
        )
