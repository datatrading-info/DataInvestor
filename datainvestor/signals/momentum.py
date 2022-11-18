import numpy as np
import pandas as pd

from datainvestor.signals.signal import Signal


class MomentumSignal(Signal):
    """
    Classe di indicatori per calcolare lo momentum nel periodo
    di ricerca (basato sul rendimento cumulativo degli ultimi
    N periodi) per un insieme di prezzi.

    Se il numero di rendimenti disponibili è inferiore al parametro
    lookback, il momentum viene calcolato su questo sottoinsieme.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e ora di inizio (UTC) del segnale.
    universe : `Universe`
        L'universo degli asset per cui calcolare i segnali.
    lookbacks : `list[int]`
        Il numero di periodi di ricerca.
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

    def _cumulative_return(self, asset, lookback):
        """
        Calcola i rendimenti cumulativi per il periodo di
        ricerca fornito ("momentum") in base ai buffer
        dei prezzi per un determinato asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            Il rendimento cumulativo ("momentum") per il periodo.
        """
        series = pd.Series(
            self.buffers.prices[MomentumSignal._asset_lookback_key(asset, lookback)]
        )
        returns = series.pct_change().dropna().to_numpy()

        if len(returns) < 1:
            return 0.0
        else:
            return (np.cumprod(1.0 + np.array(returns)) - 1.0)[-1]

    def __call__(self, asset, lookback):
        """
        Calcola il momentum per il periodo di ricerca
        per l'asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            The momentum for the period.
        """
        return self._cumulative_return(asset, lookback)
