from abc import ABCMeta, abstractmethod

from datainvestor.signals.buffer import AssetPriceBuffers


class Signal(object):
    """
    Classe astratta per fornire segnali basati su una finestra mobile
    dei prezzi utilizzando i "buffer" basati sulla coda dei prezzi.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e ora di inizio (UTC) del segnale.
    universe : `Universe`
        L'universo degli asset per cui calcolare i segnali.
    lookbacks : `list[int]`
        Il numero di periodi di ricerca per cui archiviare i prezzi.
    """

    __metaclass__ = ABCMeta

    def __init__(self, start_dt, universe, lookbacks):
        self.start_dt = start_dt
        self.universe = universe
        self.lookbacks = lookbacks
        self.assets = self.universe.get_assets(start_dt)
        self.buffers = self._create_asset_price_buffers()

    def _create_asset_price_buffers(self):
        """
        Crea un'istanza di AssetPriceBuffers.

        Returns
        -------
        `AssetPriceBuffers`
            Memorizza i buffer dei prezzi degli asset per il segnale.
        """
        return AssetPriceBuffers(
            self.assets, lookbacks=self.lookbacks
        )

    def append(self, asset, price):
        """
        Aggiunge un nuovo prezzo al buffer dei prezzi
        per l'asset specifica fornita.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        price : `float`
            Il nuovo prezzo dell'asset
        """
        self.buffers.append(asset, price)

    def update_assets(self, dt):
        """
        Assicura che tutte le nuove aggiunte all'universo ricevano
        anche un buffer di prezzo nel momento in cui entrano.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp di aggiornamento per il segnale.
        """
        universe_assets = self.universe.get_assets(dt)

        # TODO: Supponiamo che l'universo non diminuisca mai per ora
        extra_assets = list(set(universe_assets) - set((self.assets)))
        for extra_asset in extra_assets:
            self.assets.append(extra_asset)

    @abstractmethod
    def __call__(self, asset, lookback):
        raise NotImplementedError(
            "Should implement __call__()"
        )
