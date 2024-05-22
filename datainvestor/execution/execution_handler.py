class ExecutionHandler(object):
    """
    Gestisce l'esecuzione di un elenco di ordini emessi
    dal PortfolioConstructionModel tramite il Broker.

    Parameters
    ----------
    broker : `Broker`
        L'istanza Broker derivata su cui eseguire gli ordini.
    broker_portfolio_id : `str`
        Il portafoglio specifico del Broker su cui eseguire l'esecuzione.
    universe : `Universe`
         L'istanza di Universe derivata da cui ottenere l'elenco degli asset.
    submit_orders : `Boolean`, optional
        Se inviare effettivamente gli ordini al Broker o scartarli.
        Il valore predefinito è False -> Non inviare ordini.
    execution_algo : `ExecutionAlgorithm`, optional
        L'istanza derivata ExecutionAlgorithm da utilizzare per
        la strategia di esecuzione.
    data_handler : `DataHandler`, optional
        Le istanze di DataHandler derivate utilizzate (facoltativamente) per
        ottenere i dati necessari per la strategia di esecuzione.
    """

    def __init__(
        self,
        broker,
        broker_portfolio_id,
        universe,
        submit_orders=False,
        execution_algo=None,
        data_handler=None
    ):
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.universe = universe
        self.submit_orders = submit_orders
        self.execution_algo = execution_algo
        self.data_handler = data_handler

    def _apply_execution_algo_to_rebalances(self, dt, rebalance_orders):
        """
        Genera un nuovo elenco di Ordini in base alla strategia
         di esecuzione appropriata.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora corrente utilizzata per popolare le istanze dell'ordine.
        rebalance_orders : `list[Order]`
            L'elenco degli ordini di ribilanciamento da eseguire.

        Returns
        -------
        `list[Order]`
            L'elenco finale degli ordini da inviare al Broker da eseguire.
        """
        return self.execution_algo(dt, rebalance_orders)

    def __call__(self, dt, rebalance_orders):
        """
        Take the list of rebalanced Orders generated from the
        portfolio construction process and execute them at the
        Broker, via the appropriate execution algorithm.
        Prende l'elenco degli Ordini ribilanciati generati dal
        processo di costruzione del portafoglio ed li esegue
        presso il Broker, tramite l'apposito algoritmo di esecuzione.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora corrente utilizzata per popolare le istanze dell'ordine.
        rebalance_orders : `list[Order]`
            L'elenco degli ordini di ribilanciamento da eseguire.

        Returns
        -------
        `None`
        """
        final_orders = self._apply_execution_algo_to_rebalances(
            dt, rebalance_orders
        )

        # Se viene specificato l'invio dell'ordine, allora invia
        # i singoli ordini all'istanza del broker
        if self.submit_orders:
            for order in final_orders:
                self.broker.submit_order(self.broker_portfolio_id, order)
                self.broker.update(dt)