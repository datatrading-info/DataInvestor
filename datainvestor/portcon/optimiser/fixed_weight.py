from datainvestor.portcon.optimiser.optimiser import PortfolioOptimiser


class FixedWeightPortfolioOptimiser(PortfolioOptimiser):
    """
    Produce un dizionario indicizzati con gli Asset che utilizza
    direttamente i pesi. Questo semplicemente 'passa attraverso'
    i pesi forniti senza modifiche.

    Parameters
    ----------
    data_handler : `DataHandler`, optional
        Un DataHandler opzionale utilizzato per preservare l'interfaccia
        attraverso i TargetWeightGenerators.
    """

    def __init__(
        self,
        data_handler=None
    ):
        self.data_handler = data_handler

    def __call__(self, dt, initial_weights):
        """
        Produce il dizionario dei valori dei pesi target per
        ciascuna delle istanze di asset fornite.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Timestamp 'now' utilizzato per ottenere i dati appropriati
            per i pesi target.
        initial_weights : `dict{str: float}`
            I pesi iniziali prima dell'ottimizzazione.

        Returns
        -------
        `dict{str: float}`
            I valori scalari dei pesi target indicizzati per ogni simbolo di asset
        """
        return initial_weights
