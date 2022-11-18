from collections import deque


class AssetPriceBuffers(object):
    """
    Classe di utilità per memorizzare buffer di prezzo basato
    su code a doppia estremità ("deque") da utilizzare nei
    calcoli degli indicatori basati su lookback.

    Parameters
    ----------
    assets : `list[str]`
        L'elenco degli asset per i quali creare buffer di prezzo.
    lookbacks : `list[int]`, optional
        Il numero di periodi di ricerca per cui archiviare i prezzi.
    """

    def __init__(self, assets, lookbacks=[12]):
        self.assets = assets
        self.lookbacks = lookbacks
        self.prices = self._create_all_assets_prices_buffer_dict()

    @staticmethod
    def _asset_lookback_key(asset, lookback):
        """
        Crea la chiave di ricerca del dizionario del buffer
        in base al nome dell'asset e al periodo di ricerca.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di lookback.

        Returns
        -------
        `str`
            La chiave di ricerca.
        """
        return '%s_%s' % (asset, lookback)

    def _create_single_asset_prices_buffer_dict(self, asset):
        """
        Crea un dizionario di buffer di prezzo della
        coppia asset-lookback per un singolo asset.

        Returns
        -------
        `dict{str: deque[float]}`
            Il dizionario del buffer dei prezzi.
        """
        return {
            AssetPriceBuffers._asset_lookback_key(
                asset, lookback
            ): deque(maxlen=lookback)
            for lookback in self.lookbacks
        }

    def _create_all_assets_prices_buffer_dict(self):
        """
        Crea un dizionario di buffer di prezzo della
        coppia asset-lookback per tutti gli asset.

        Returns
        -------
        `dict{str: deque[float]}`
            Il dizionario del buffer dei prezzi.
        """
        prices = {}
        for asset in self.assets:
            prices.update(self._create_single_asset_prices_buffer_dict(asset))
        return prices

    def add_asset(self, asset):
        """
        Aggiungere un asset all'elenco degli asset correnti. E' necessario se
        l'asset fa parte di un DynamicUniverse e non è presente all'inizio
        di un backtest.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        """
        if asset in self.assets:
            raise ValueError(
                'Unable to add asset "%s" since it already '
                'exists in this price buffer.' % asset
            )
        else:
            self.prices.update(self._create_single_asset_prices_buffer_dict(asset))

    def append(self, asset, price):
        """
        Aggiungere un nuovo prezzo alla coda dei prezzi
        per l'asset specifico fornito.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        price : `float`
            Il nuovo prezzo per l'asset.
        """
        if price <= 0.0:
            raise ValueError(
                'Unable to append non-positive price of "%0.2f" '
                'to metrics buffer for Asset "%s".' % (price, asset)
            )

        # L'asset potrebbe essere stato aggiunto all'universo dopo
        # l'inizio del backtest e quindi bisogna creare un nuovo
        # buffer dei prezzi
        asset_lookback_key = AssetPriceBuffers._asset_lookback_key(asset, self.lookbacks[0])
        if asset_lookback_key not in self.prices:
            self.prices.update(self._create_single_asset_prices_buffer_dict(asset))

        for lookback in self.lookbacks:
            self.prices[
                AssetPriceBuffers._asset_lookback_key(
                    asset, lookback
                )
            ].append(price)
