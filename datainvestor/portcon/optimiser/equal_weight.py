from datainvestor.portcon.optimiser.optimiser import PortfolioOptimiser


class EqualWeightPortfolioOptimiser(PortfolioOptimiser):
    """
    Produce un dizionario indicizzato per Asset con pesi uguali (facoltativamente)
    ridimensionati. Senza ridimensionamento, questo viene normalizzato per
    garantire le somme vettoriali all'unità. Questo sostituisce i pesi forniti
    nel dizionario initial_weights.

    Parameters
    ----------
    scale : `float`, optional
        Un fattore di scala opzionale per regolare i pesi. Altrimenti il
        vettore è impostato per sommare all'unità.
    data_handler : `DataHandler`, optional
        Un DataHandler opzionale utilizzato per preservare l'interfaccia
        tra PortfolioOptimiser.
    """

    def __init__(
        self,
        scale=1.0,
        data_handler=None
    ):
        self.scale = scale
        self.data_handler = data_handler

    def __call__(self, dt, initial_weights):
        """
        Produce the dictionary of single fixed scalar target weight
        values for each of the Asset instances provided.
        Produce il dizionario dei singoli valori scalari fissi dei pesi
        target per ciascuna delle istanze di asset fornite.

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
            I valori scalari dei pesi target indicizzati per
            ogni simbolo degli asset
        """
        assets = initial_weights.keys()
        num_assets = len(assets)
        equal_weight = 1.0 / float(num_assets)
        scaled_equal_weight = self.scale * equal_weight
        return {asset: scaled_equal_weight for asset in assets}
