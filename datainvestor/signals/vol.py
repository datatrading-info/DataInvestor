import numpy as np
import pandas as pd

from datainvestor.signals.signal import Signal


class VolatilitySignal(Signal):
    """
    Classe di indicatori per calcolare la volatilità giornaliera dei
    rendimenti nel periodo di previsione, che viene poi annualizzata.

    Se il numero di rendimenti disponibili è inferiore al parametro
    lookback, la volatilità viene calcolata su questo sottoinsieme.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e ora di inizio (UTC) del segnale.
    universe : `Universe`
        L'universo degli asset per cui calcolare i segnali.
    lookbacks : `list[int]`
        Il numero di periodi di ricerca per cui archiviare i prezzi.
    """

    def __init__(self, start_dt, universe, lookbacks):
        bumped_lookbacks = [lookback + 1 for lookback in lookbacks]
        super().__init__(start_dt, universe, bumped_lookbacks)

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
            Il periodo di ricerca.

        Returns
        -------
        `str`
            La chiave di ricerca.
        """
        return '%s_%s' % (asset, lookback + 1)

    def _annualised_vol(self, asset, lookback):
        """
        Calcola la volatilità annualizzata per il periodo di riferimento
        fornito in base ai buffer di prezzo per un determinato asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            La volatilità annualizzata dei rendimenti.
        """
        series = pd.Series(
            self.buffers.prices[
                VolatilitySignal._asset_lookback_key(
                    asset, lookback
                )
            ]
        )
        returns = series.pct_change().dropna().to_numpy()

        if len(returns) < 1:
            return 0.0
        else:
            return np.std(returns) * np.sqrt(252)

    def __call__(self, asset, lookback):
        """
        Calcola la volatilità annualizzata dei rendimenti per l'asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            La volatilità annualizzata dei rendimenti.
        """
        return self._annualised_vol(asset, lookback)
