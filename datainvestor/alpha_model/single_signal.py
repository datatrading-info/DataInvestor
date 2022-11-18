from datainvestor.alpha_model.alpha_model import AlphaModel


class SingleSignalAlphaModel(AlphaModel):
    """
    Un semplice AlphaModel che fornisce un singolo valore scalare
    di previsione per ogni Asset nell'Universo.

    Parameters
    ----------
    universe : `Universe`
        Gli asset su cui produrre i segnali
    signal : `float`, optional
        Il singolo fisso valore a virgola mobile per i segnali
    data_handler : `DataHandler`, optional
        Un DataHandler opzionale usato per preservare l'interfaccia attraverso gli AlphaModels.
    """

    def __init__(
        self,
        universe,
        signal=1.0,
        data_handler=None
    ):
        self.universe = universe
        self.signal = signal
        self.data_handler = data_handler

    def __call__(self, dt):
        """
        Produce il dizionario dei segnali fissi scalari per
        ciascuna delle istanze Asset all'interno dell'Universo.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il tempo 'now' usato per ottenere specifici dati e universo
            per i segnali.

        Returns
        -------
        `dict{str: float}`
            Un dizionario di valori scalari di segnali per ogni simbolo di asset
        """
        assets = self.universe.get_assets(dt)
        return {asset: self.signal for asset in assets}
