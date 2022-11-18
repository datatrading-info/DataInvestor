from datainvestor.asset.universe.universe import Universe


class DynamicUniverse(Universe):
    """
    Un universo di asset che consente l'aggiunta di asset
    oltre un certo datetime.

    TODO: attualmente non supporta la rimozione delle risorse
     o sequenze di aggiunte/rimozioni.

    Parameters
    ----------
    asset_dates : `dict{str: pd.Timestamp}`
        Mappa di asset e le relative date di entrata
    """

    def __init__(self, asset_dates):
        self.asset_dates = asset_dates

    def get_assets(self, dt):
        """
        Ottienere l'elenco degli asset nell'Universo in un determinato momento.
        Questo restituirà sempre un elenco statico indipendente dal timestamp fornito.

        Se non viene fornita alcuna data, non includere l'asset. Restituisce solo gli
        asset per cui la data e l'ora corrente supera la data e l'ora fornita.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp in cui recuperare l'elenco delgli asset.

        Returns
        -------
        `list[str]`
            La lista dei simboli degli asset nell'universo statico.
        """
        return [
            asset for asset, asset_date in self.asset_dates.items()
            if asset_date is not None and dt >= asset_date
        ]
