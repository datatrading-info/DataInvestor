from datainvestor.execution.execution_algo.execution_algo import ExecutionAlgorithm


class MarketOrderExecutionAlgorithm(ExecutionAlgorithm):
    """
    Semplice algoritmo di esecuzione che crea un elenco non modificato
    di Ordini di mercato dagli Ordini di ribilanciamento.
    """

    def __call__(self, dt, initial_orders):
        """
        Restituisce semplicemente l'elenco degli ordini iniziali in modalità 'pass through'.

        Parameters
        ----------
        dt : `pd.Timestamp`
            L'ora corrente utilizzata per popolare le istanze dell'ordine.
        rebalance_orders : `list[Order]`
            L'elenco degli ordini di ribilanciamento da eseguire.

        Returns
        -------
        `list[Order]`
            L'elenco finale degli ordini da inviare al Broker per  l'esecuzione
        """
        return initial_orders
