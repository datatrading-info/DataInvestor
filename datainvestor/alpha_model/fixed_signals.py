from datainvestor.alpha_model.alpha_model import AlphaModel


class FixedSignalsAlphaModel(AlphaModel):
    """
    Un semplice AlphaModel che fornisce un singolo valore scalare
    di previsione per ogni Asset nell'Universo.

    Parameters
    ----------
    signal_weights : `dict{str: float}`
        I pesi dei segnali per ogni simbolo di asset
    universe : `Universe`, optional
        Gli asset su cui produrre i segnali
    data_handler : `DataHandler`, optional
        Un DataHandler opzionale usato per preservare l'interfaccia attraverso gli AlphaModels.
    """

    def __init__(
        self,
        signal_weights,
        universe=None,
        data_handler=None
    ):
        self.signal_weights = signal_weights
        self.universe = universe
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
        return self.signal_weights
