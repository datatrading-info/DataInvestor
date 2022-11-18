from datainvestor.execution.execution_handler import (
    ExecutionHandler
)
from datainvestor.execution.execution_algo.market_order import (
    MarketOrderExecutionAlgorithm
)
from datainvestor.portcon.pcm import (
    PortfolioConstructionModel
)
from datainvestor.portcon.optimiser.fixed_weight import (
    FixedWeightPortfolioOptimiser
)
from datainvestor.portcon.order_sizer.dollar_weighted import (
    DollarWeightedCashBufferedOrderSizer
)
from datainvestor.portcon.order_sizer.long_short import (
    LongShortLeveragedOrderSizer
)


class QuantTradingSystem(object):
    """
    Incapsula tutti i componenti associati al sistema di trading quantitativo.
    Ciò include il modello alphaa, il modello di rischio, il modello dei costi di
    transazione insieme al meccanismo di costruzione ed esecuzione del portafoglio.

    Parameters
    ----------
    universe : `Universe`
        L'universo degli Asset.
    broker : `Broker`
        Il Broker dove eseguire gli ordini.
    broker_portfolio_id : `str`
        Il portafoglio specifico presso il Broker dove inviare gli ordini.
    data_handler : `DataHandler`
        Il data handler usato per tutti i dati di mercato e fondamentali.
    alpha_model : `AlphaModel`
        The alpha model used within the portfolio construction.
        Il modello di segnale alphaa/previsione per la costruzione del portafoglio.
    risk_model : `AlphaModel`, optional
        Il modello di rischio per la costruzione del portafoglio.
    long_only : `Boolean`, optional
        Se invocare il dimensionatore di ordini long only o consentire portafogli
        con leva long/short. L'impostazione predefinita è long/short con leva.
    submit_orders : `Boolean`, optional
        Se inviare effettivamente gli ordini generati. Predefinito per nessun invio.
    """

    def __init__(
        self,
        universe,
        broker,
        broker_portfolio_id,
        data_handler,
        alpha_model,
        *args,
        risk_model=None,
        long_only=False,
        submit_orders=False,
        **kwargs
    ):
        self.universe = universe
        self.broker = broker
        self.broker_portfolio_id = broker_portfolio_id
        self.data_handler = data_handler
        self.alpha_model = alpha_model
        self.risk_model = risk_model
        self.long_only = long_only
        self.submit_orders = submit_orders
        self._initialise_models(**kwargs)

    def _create_order_sizer(self, **kwargs):
        """
        Depending upon whether the quant trading system has been
        set to be long only, determine the appropriate order sizing
        mechanism.

        Returns
        -------
        `OrderSizer`
            The order sizing mechanism for the portfolio construction.
        """
        if self.long_only:
            if 'cash_buffer_percentage' not in kwargs:
                raise ValueError(
                    'Long only portfolio specified for Quant Trading System '
                    'but no cash buffer percentage supplied.'
                )
            cash_buffer_percentage = kwargs['cash_buffer_percentage']

            order_sizer = DollarWeightedCashBufferedOrderSizer(
                self.broker,
                self.broker_portfolio_id,
                self.data_handler,
                cash_buffer_percentage=cash_buffer_percentage
            )
        else:
            if 'gross_leverage' not in kwargs:
                raise ValueError(
                    'Long/short leveraged portfolio specified for Quant '
                    'Trading System but no gross leverage percentage supplied.'
                )
            gross_leverage = kwargs['gross_leverage']

            order_sizer = LongShortLeveragedOrderSizer(
                self.broker,
                self.broker_portfolio_id,
                self.data_handler,
                gross_leverage=gross_leverage
            )

        return order_sizer

    def _initialise_models(self, **kwargs):
        """
        Initialise the various models for the quantitative
        trading strategy. This includes the portfolio
        construction and the execution.

        TODO: Add TransactionCostModel
        TODO: Ensure this is dynamically generated from config.
        """
        # Determine the appropriate order sizing mechanism
        order_sizer = self._create_order_sizer(**kwargs)

        # TODO: Allow optimiser to be generated from config
        optimiser = FixedWeightPortfolioOptimiser(
            data_handler=self.data_handler
        )

        # Generate the portfolio construction
        self.portfolio_construction_model = PortfolioConstructionModel(
            self.broker,
            self.broker_portfolio_id,
            self.universe,
            order_sizer,
            optimiser,
            alpha_model=self.alpha_model,
            risk_model=self.risk_model,
            data_handler=self.data_handler
        )

        # Execution
        execution_algo = MarketOrderExecutionAlgorithm()
        self.execution_handler = ExecutionHandler(
            self.broker,
            self.broker_portfolio_id,
            self.universe,
            submit_orders=self.submit_orders,
            execution_algo=execution_algo,
            data_handler=self.data_handler
        )

    def __call__(self, dt, stats=None):
        """
        Construct the portfolio and (optionally) execute the orders
        with the broker.

        Parameters
        ----------
        dt : `pd.Timestamp`
            The current time.
        stats : `dict`, optional
            An optional statistics dictionary to append values to
            throughout the simulation lifetime.

        Returns
        -------
        `None`
        """
        # Construct the target portfolio
        rebalance_orders = self.portfolio_construction_model(dt, stats=stats)

        # Execute the orders
        self.execution_handler(dt, rebalance_orders)
