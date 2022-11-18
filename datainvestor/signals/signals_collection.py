class SignalsCollection(object):
    """
    Fornisce un meccanismo per aggregare tutti i segnali
    utilizzati da AlphaModels o RiskModels.

    Tiene traccia dell'aggiornamento dell'universo degli asset
    per ogni segnale se viene utilizzato un DynamicUniverse.

    Garantisce che ogni segnale riceva un nuovo punto dati alla
    velocità di iterazione della simulazione appropriata.

    Parameters
    ----------
    signals : `dict{str: Signal}`
        Mappa del nome del segnale all'istanza derivata di Signal
    data_handler : `DataHandler`
        Il gestore dati utilizzato per ottenere i prezzi.
    """

    def __init__(self, signals, data_handler):
        self.signals = signals
        self.data_handler = data_handler
        self.warmup = 0  # Used for 'burn in'

    def __getitem__(self, signal):
        """
        Consenti a Signal di essere restituito tramite
        una sintassi simile a un dizionario.

        Parameters
        ----------
        signal : `str`
            La stringa di segnale.

        Returns
        -------
        `Signal`
            L'istanza del segnale.
        """
        return self.signals[signal]

    def update(self, dt):
        """
        Aggiorna l'universo (se dinamico) per ogni segnale e le
        informazioni sui prezzi per questo timestamp.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora in cui i segnali devono essere aggiornati.
        """
        # Assicura che tutti i nuovi asset in un DynamicUniverse
        # siano aggiunte al segnale
        for name, signal in self.signals.items():
            self.signals[name].update_assets(dt)

        # Aggiorna tutti i segnali con nuovi prezzi
        for name, signal in self.signals.items():
            assets = signal.assets
            for asset in assets:
                price = self.data_handler.get_asset_latest_mid_price(dt, asset)
                self.signals[name].append(asset, price)
        self.warmup += 1
