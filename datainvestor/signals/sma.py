import numpy as np

from datainvestor.signals.signal import Signal


class SMASignal(Signal):
    """
    Classe di indicatori per calcolare la media mobile semplice
    degli ultimi N periodi per un insieme di prezzi.

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
        super().__init__(start_dt, universe, lookbacks)

    def _simple_moving_average(self, asset, lookback):
        """
        Calcola il "trend" per il periodo di ricerca fornito
        in base alla media mobile semplice del buffer dei
        prezzi per un determinato asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            Il valore SMA ('trend') per il periodo.
        """
        return np.mean(self.buffers.prices['%s_%s' % (asset, lookback)])

    def __call__(self, asset, lookback):
        """
        Calcola l'andamento del periodo di
        ricerca per l'asset.

        Parameters
        ----------
        asset : `str`
            Il nome del simbolo dell'asset.
        lookback : `int`
            Il periodo di ricerca.

        Returns
        -------
        `float`
            Il trend (SMA) per il periodo.
        """
        return self._simple_moving_average(asset, lookback)
