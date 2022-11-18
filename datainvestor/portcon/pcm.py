from datainvestor import settings
from datainvestor.execution.order import Order


class PortfolioConstructionModel(object):
    """
    Incapsula il processo di generazione di un vettore di pesi target per
    un universo di asset, basato sull'input di un AlphaModel, un RiskModel
    e un TransactionCostModel.

    Il processo di ottimizzazione è delegato a un'istanza
    TargetWeightGenerator fornita dal sistema.

    Parameters
    ----------
    broker : `Broker`
        L'istanza Broker derivata da cui ottenere il portafoglio corrente.
    broker_portfolio_id : `str`
        Il portafoglio specifico presso il Broker da cui ottenere posizioni.
    universe : `Universe`
        L'Universo su cui costruire un portfolio.
    order_sizer : `OrderSizeGenerator`
       Converte i pesi target in posizioni integrali.
    optimiser : `PortfolioOptimiser`
         Il meccanismo di ottimizzazione per la generazione dei pesi target.
    alpha_model : `AlphaModel`, optional
        Il modello di segnale alphaa/previsione per gli asset nell'universo.
    risk_model : `RiskModel`, optional
        Il modello di rischio per gli asset nell'universo.
    cost_model : `TransactionCostModel`, optional
        Il modello dei costi di transazione per gli asset nell'universo.
    data_handler : `DataHandler`, optional
        Il data handler usato per la costruzione del portafoglio.
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        universe,
        order_sizer,
        optimiser,
        alpha_model=None,
        risk_model=None,
        cost_model=None,
        data_handler=None,
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.universe = universe
        self.order_sizer = order_sizer
        self.optimiser = optimiser
        self.alpha_model = alpha_model
        self.risk_model = risk_model
        self.cost_model = cost_model
        self.data_handler = data_handler

    def _obtain_full_asset_list(self, dt):
        """
        Crea un'unione tra gli Asset nell'Universo attuale e
        quelli nel Portfolio Broker.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora corrente utilizzata per ottenere gli asset dell'universo.

        Returns
        -------
        `list[str]`
            L'elenco completo ordinato delle stringhe di simboli asset.
        """
        broker_portfolio = self.broker.get_portfolio_as_dict(
            self.broker_portfolio_id
        )
        broker_assets = list(broker_portfolio.keys())
        universe_assets = self.universe.get_assets(dt)
        return sorted(
            list(
                set(broker_assets).union(set(universe_assets))
            )
        )

    def _create_zero_target_weight_vector(self, full_assets):
        """
        Crea un vettore iniziale di pesi target zero per tutte gli asset
        sia nel portafoglio broker che nell'universo corrente.

        Parameters
        ----------
        full_assets : `list[str]`
            L'elenco completo dei simboli degli asset.

        Returns
        -------
        `dict{str: float}`
            Il vettore dei pesi target zero per tutti gli asset.
        """
        return {asset: 0.0 for asset in full_assets}

    def _create_full_asset_weight_vector(self, zero_weights, optimised_weights):
        """
        Assicura che tutti gli asset nel portafoglio del broker siano esauriti
        se non sono specificatamente referenziati sui pesi ottimizzati.


        Parameters
        ----------
        zero_weights : `dict{str: float}`
            L'elenco completo degli asset, tutti con pesi zero.
        optimised_weights : `dict{str: float}`
            L'elenco dei pesi per gli asset con un peso diverso da zero.
            Sostituisce i pesi zero dove le chiavi si intersecano.


        Returns
        -------
        `dict{str: float}`
            L'unione dei pesi zero e dei pesi ottimizzati, dove i pesi
            ottimizzati hanno la precedenza.
        """
        return {**zero_weights, **optimised_weights}

    def _generate_target_portfolio(self, dt, weights):
        """
        Generate the number of units (shares/lots) per Asset based on the
        target weight vector.
        Genera il numero di unità (azioni/lotti) per asset in base al
        vettore dei pesi target.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp corrente.
        weights : `dict{str: float}`
            L'unione dei pesi zero e dei pesi ottimizzati, dove i pesi
            ottimizzati hanno la precedenza.

        Returns
        -------
        `dict{str: dict}`
            Quantità di asset target in unità integrali.
        """
        return self.order_sizer(dt, weights)

    def _obtain_current_portfolio(self):
        """
        Richiede al broker le quantità di asset del conto e li
        restituisce come dizionario di portafoglio.

        Returns
        -------
        `dict{str: dict}`
            Quantità di asset del conto del broker in unità integrali.
        """
        return self.broker.get_portfolio_as_dict(self.broker_portfolio_id)

    def _generate_rebalance_orders(
        self,
        dt,
        target_portfolio,
        current_portfolio
    ):
        """
        Crea un elenco incrementale di ordini di ribilanciamento dal target
        fornito e dai portafogli correnti.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora corrente utilizzata per popolare le istanze dell'ordine.
        target_portfolio : `dict{str: dict}`
            Quantità di asset target in unità integrali.
        curent_portfolio : `dict{str: dict}`
            Quantità di asset correnti (nel broker) in unità integrali.

        Returns
        -------
        `list[Order]`
            L'elenco degli Ordini di ribilanciamento
        """

        # Imposta tutti gli asset del portafoglio di destinazione
        # che non sono nel portafoglio corrente su una quantità
        # zero all'interno del portafoglio corrente
        for asset in target_portfolio:
            if asset not in current_portfolio:
                current_portfolio[asset] = {"quantity": 0}

        # Imposta tutti gli asset del portafoglio corrente che non sono
        # nel portafoglio di destinazione (e non sono contanti) su una
        # quantità zero all'interno del portafoglio di destinazione
        for asset in current_portfolio:
            if type(asset) != str:
                if asset not in target_portfolio:
                    target_portfolio[asset] = {"quantity": 0}

        # Scorre l'elenco degli asset e crea le quantità di differenza
        # richieste per ciascuna risorsa
        rebalance_portfolio = {}
        for asset in target_portfolio.keys():
            target_qty = target_portfolio[asset]["quantity"]
            current_qty = current_portfolio[asset]["quantity"]
            order_qty = target_qty - current_qty
            rebalance_portfolio[asset] = {"quantity": order_qty}

        # Crea l'elenco degli ordini di ribilanciamento dal portafoglio
        # ordini solo dove le quantità sono diverse da zero
        rebalance_orders = [
            Order(dt, asset, rebalance_portfolio[asset]["quantity"])
            for asset, asset_dict in sorted(
                rebalance_portfolio.items(), key=lambda x: x[0]
            )
            if rebalance_portfolio[asset]["quantity"] != 0
        ]

        return rebalance_orders

    def _create_zero_target_weights_vector(self, dt):
        """
        Determina l'universo di asset alla data e ora fornita e
        utilizzarlo per generare un vettore di pesi di valore scalare
        zero per ciascun asset.

        Parameters
        ----------
        dt : `pd.Timestamp`
            La data e l'ora utilizzata per determinare l'elenco degli asset
        Returns
        -------
        `dict{str: float}`
            Il vettore dei peso zero indicizzato dal simbolo Asset.
        """
        assets = self.universe.get_assets(dt)
        return {asset: 0.0 for asset in assets}

    def __call__(self, dt, stats=None):
        """
        Esegue il processo di costruzione del portafoglio in una data
        e ora specificata.

        Utilizza le istanze del modello alpha, del modello di rischio e del modello
        dei costi per creare un elenco di pesi desiderati che vengono quindi
        inviati all'istanza del generatore di pesi target per l'ottimizzazione.

        Parameters
        ----------
        dt : `pd.Timestamp`
            La data e l'ora utilizzata per la determinazione dell'elenco
            degli asset e la generazione dei pesi.
        stats : `dict`, optional
            Un dizionario statistico opzionale a cui aggiungere valori
            per tutta la durata della simulazione.

        Returns
        -------
        `list[Order]`
            L'elenco degli ordini di ribilanciamento da inviare in Esecuzione.
        """
        # Se viene fornito un AlphaModel, usa i suoi suggerimenti, altrimenti
        # crea un vettore di peso nullo (zero per tutti gli asset).
        if self.alpha_model:
            weights = self.alpha_model(dt)
        else:
            weights = self._create_zero_target_weights_vector(dt)

        # Se è presente un modello di rischio, utilizzarlo per
        # sovrascrivere potenzialmente i pesi del modello alpha
        if self.risk_model:
            weights = self.risk_model(dt, weights)

        # Eseguire l'ottimizzazione del portafoglio
        optimised_weights = self.optimiser(dt, initial_weights=weights)

        # Garantire che tutti gli asset nel portafoglio del broker siano esauriti
        # se non sono specificatamente referenziati sui pesi ottimizzati
        full_assets = self._obtain_full_asset_list(dt)
        full_zero_weights = self._create_zero_target_weight_vector(full_assets)
        full_weights = self._create_full_asset_weight_vector(
            full_zero_weights, optimised_weights
        )
        if settings.PRINT_EVENTS:
            print(
                "(%s) - target weights: %s" % (dt, full_weights)
            )

        # TODO: Miglioralo con un gestore completo di looging delle statistiche completo
        if stats is not None:
            alloc_dict = {'Date': dt}
            alloc_dict.update(full_weights)
            stats['target_allocations'].append(alloc_dict)

        # Calcola il portafoglio target in nozionale
        target_portfolio = self._generate_target_portfolio(dt, full_weights)

        # Ottiene il portafoglio dei conti del broker
        current_portfolio = self._obtain_current_portfolio()

        # Crea ordini di ribilanciamento
        rebalance_orders = self._generate_rebalance_orders(
            dt, target_portfolio, current_portfolio
        )
        # TODO: Implementare il modello dei costi

        return rebalance_orders
