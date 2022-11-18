from datainvestor.asset.universe.universe import Universe


class StaticUniverse(Universe):
    """
    Un universo di asset che non consente modifiche alla sua
    composione attraverso il tempo.

    Parameters
    ----------
    asset_list : `list[str]`
        La lista dei simboli degli asset che forma StaticUniverse.
    """

    def __init__(self, asset_list):
        self.asset_list = asset_list

    def get_assets(self, dt):
        """
        Ottienere l'elenco degli asset nell'Universo in un determinato momento.
        Questo restituirà sempre un elenco statico indipendente dal timestamp fornito.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp in cui recuperare l'elenco delgli asset.

        Returns
        -------
        `list[str]`
            La lista dei simboli degli asset nell'universo statico.
        """
        return self.asset_list
