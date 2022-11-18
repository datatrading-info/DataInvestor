import os

import pandas as pd

from datainvestor.asset.equity import Equity
from datainvestor.broker.simulated_broker import SimulatedBroker
from datainvestor.broker.fee_model.zero_fee_model import ZeroFeeModel
from datainvestor.data.backtest_data_handler import BacktestDataHandler
from datainvestor.data.daily_bar_csv import CSVDailyBarDataSource
from datainvestor.exchange.simulated_exchange import SimulatedExchange
from datainvestor.simulation.daily_bday import DailyBusinessDaySimulationEngine
from datainvestor.system.qts import QuantTradingSystem
from datainvestor.system.rebalance.buy_and_hold import BuyAndHoldRebalance
from datainvestor.system.rebalance.daily import DailyRebalance
from datainvestor.system.rebalance.end_of_month import EndOfMonthRebalance
from datainvestor.system.rebalance.weekly import WeeklyRebalance
from datainvestor.trading.trading_session import TradingSession
from datainvestor import settings

DEFAULT_ACCOUNT_NAME = 'Backtest Simulated Broker Account'
DEFAULT_PORTFOLIO_ID = '000001'
DEFAULT_PORTFOLIO_NAME = 'Backtest Simulated Broker Portfolio'


class BacktestTradingSession(TradingSession):
    """
    Incapsula un backtest completo di simulazione di trading con istanze
    per ciascun modulo fornite esternamente.

    Utilizza impostazioni predefinite ragionevoli per consentire il backtesting
    diretto di strategie di trading meno complesse.

    Parameters
    ----------
    start_dt : `pd.Timestamp`
        La data e ora di inizio (UTC) del backtest.
    end_dt : `pd.Timestamp`
        La data e l'ora di fine (UTC) del backtest.
    universe : `Universe`
        L'universo degli asset da utilizzare per il backtest.
    alpha_model : `AlphaModel`
        Il modello alph segnale/previsione per la strategia di trading quantitativo.
    risk_model : `RiskModel`
        Il modello di rischio per la strategia di quant trading.
    signals : `SignalsCollection`, optional
        Una raccolta di segnali utilizzati nei modelli di trading.
    initial_cash : `float`, optional
        Il capitale iniziale (default a $1MM)
    rebalance : `str`, optional
        La frequenza di ribilanciamento del backtest, per impostazione predefinita "settimanale".
    account_name : `str`, optional
        Il nome dell'account broker simulato.
    portfolio_id : `str`, optional
        L'ID del portafoglio utilizzato per il backtest.
    portfolio_name : `str`, optional
        Il nome del portafoglio utilizzato per il backtest.
    long_only : `Boolean`, optional
        Se invocare il dimensionatore di ordini long only o consentire portafogli
        con leva long/short. L'impostazione predefinita è long/short con leva.
    fee_model : `FeeModel` class instance, optional
        La sottoclasse derivata da FeeModel facoltativa da utilizzare per le stime dei costi di transazione.
    burn_in_dt : `pd.Timestamp`, optional
        La data per iniziare a monitorare le statistiche della strategia, utilizzata
        per le strategie che richiedono un periodo di "burn in" dei dati
    """

    def __init__(
        self,
        start_dt,
        end_dt,
        universe,
        alpha_model,
        risk_model=None,
        signals=None,
        initial_cash=1e6,
        rebalance='weekly',
        account_name=DEFAULT_ACCOUNT_NAME,
        portfolio_id=DEFAULT_PORTFOLIO_ID,
        portfolio_name=DEFAULT_PORTFOLIO_NAME,
        long_only=False,
        fee_model=ZeroFeeModel(),
        burn_in_dt=None,
        data_handler=None,
        **kwargs
    ):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.universe = universe
        self.alpha_model = alpha_model
        self.risk_model = risk_model
        self.signals = signals
        self.initial_cash = initial_cash
        self.rebalance = rebalance
        self.account_name = account_name
        self.portfolio_id = portfolio_id
        self.portfolio_name = portfolio_name
        self.long_only = long_only
        self.fee_model = fee_model
        self.burn_in_dt = burn_in_dt

        self.exchange = self._create_exchange()
        self.data_handler = self._create_data_handler(data_handler)
        self.broker = self._create_broker()
        self.sim_engine = self._create_simulation_engine()

        if rebalance == 'weekly':
            if 'rebalance_weekday' in kwargs:
                self.rebalance_weekday = kwargs['rebalance_weekday']
            else:
                raise ValueError(
                    "Rebalance frequency was set to 'weekly' but no specific "
                    "weekday was provided. Try adding the 'rebalance_weekday' "
                    "keyword argument to the instantiation of "
                    "BacktestTradingSession, e.g. with 'WED'."
                )
        self.rebalance_schedule = self._create_rebalance_event_times()

        self.qts = self._create_quant_trading_system(**kwargs)
        self.equity_curve = []
        self.target_allocations = []

    def _is_rebalance_event(self, dt):
        """
        Verifica se il timestamp fornito fa parte del programma
        di ribilanciamento del backtest.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il timestamp per il controllo del programma di ribilanciamento.

        Returns
        -------
        `Boolean`
            Se il timestamp fa parte del programma di ribilanciamento.
        """
        return dt in self.rebalance_schedule

    def _create_exchange(self):
        """
        Genera un'istanza di exchange simulato utilizzata per il
        controllo delle ore di mercato e il calendario delle festività.

        Returns
        -------
        `SimulatedExchanage`
            L'istanza di exchange simulato.
        """
        return SimulatedExchange(self.start_dt)

    def _create_data_handler(self, data_handler):
        """
        Crea un'istanza DataHandler per caricare i dati sui prezzi degli
        asset utilizzati nel backtest.

        TODO: attualmente l'impostazione predefinita per le origini dati
        CSV è la barra giornaliera nel formato YahooFinance.

        Parameters
        ----------
        `BacktestDataHandler` or None
            L'istanza del gestore dati di backtesting.

        Returns
        -------
        `BacktestDataHandler`
            L'istanza del gestore dati di backtest.
        """
        if data_handler is not None:
            return data_handler

        try:
            os.environ['DATAINVESTOR_CSV_DATA_DIR']
        except KeyError:
            if settings.PRINT_EVENTS:
                print(
                    "The DATAINVESTOR_CSV_DATA_DIR environment variable has not been set. "
                    "This means that DataInvestor will fall back to finding data within the "
                    "current directory where the backtest has been executed. However "
                    "it is strongly recommended that a DATAINVESTOR_CSV_DATA_DIR environment "
                    "variable is set for future backtests."
                )
            csv_dir = '.'
        else:
            csv_dir = os.environ.get('DATAINVESTOR_CSV_DATA_DIR')

        # TODO: Per ora DataInvestor gestisce solo le azioni
        data_source = CSVDailyBarDataSource(csv_dir, Equity)

        data_handler = BacktestDataHandler(
            self.universe, data_sources=[data_source]
        )
        return data_handler

    def _create_broker(self):
        """
        Crea un SimulatedBroker con gli specifici identificatori
        di portafoglio predefiniti.

        Returns
        -------
        `SimulatedBroker`
            L'istanza del broker simulato.
        """
        broker = SimulatedBroker(
            self.start_dt,
            self.exchange,
            self.data_handler,
            account_id=self.account_name,
            initial_funds=self.initial_cash,
            fee_model=self.fee_model
        )
        broker.create_portfolio(self.portfolio_id, self.portfolio_name)
        broker.subscribe_funds_to_portfolio(self.portfolio_id, self.initial_cash)
        return broker

    def _create_simulation_engine(self):
        """
        Crea un'istanza del motore di simulazione per generare gli
        eventi utilizzati dall'algoritmo di quant trading su cui agire.

        TODO: attualmente codificato per eventi quotidiani

        Returns
        -------
        `SimulationEngine`
            Il motore di simulazione che genera timestamp di simulazione.
        """
        return DailyBusinessDaySimulationEngine(
            self.start_dt, self.end_dt, pre_market=False, post_market=False
        )

    def _create_rebalance_event_times(self):
        """
        Crea l'elenco dei timestamp di ribilanciamento utilizzati per determinare
        quando eseguire la strategia di trading quantitativo durante il backtest.

        Returns
        -------
        `List[pd.Timestamp]`
            L'elenco dei timestamp di ribilanciamento.
        """
        if self.rebalance == 'buy_and_hold':
            rebalancer = BuyAndHoldRebalance(self.start_dt)
        elif self.rebalance == 'daily':
            rebalancer = DailyRebalance(
                self.start_dt, self.end_dt
            )
        elif self.rebalance == 'weekly':
            rebalancer = WeeklyRebalance(
                self.start_dt, self.end_dt, self.rebalance_weekday
            )
        elif self.rebalance == 'end_of_month':
            rebalancer = EndOfMonthRebalance(self.start_dt, self.end_dt)
        else:
            raise ValueError(
                'Unknown rebalance frequency "%s" provided.' % self.rebalance
            )
        return rebalancer.rebalances

    def _create_quant_trading_system(self, **kwargs):
        """
        Crea il sistema di trading quantitativo con il modello alpha fornito.

        TODO: Tutta la costruzione/ottimizzazione del portafoglio è codificata per default.

        Returns
        -------
        `QuantTradingSystem`
            Il sistema di trading quantitativo.
        """
        if self.long_only:
            if 'cash_buffer_percentage' not in kwargs:
                raise ValueError(
                    'Long only portfolio specified for Quant Trading System '
                    'but no cash buffer percentage supplied.'
                )
            cash_buffer_percentage = kwargs['cash_buffer_percentage']

            qts = QuantTradingSystem(
                self.universe,
                self.broker,
                self.portfolio_id,
                self.data_handler,
                self.alpha_model,
                self.risk_model,
                long_only=self.long_only,
                cash_buffer_percentage=cash_buffer_percentage,
                submit_orders=True
            )
        else:
            if 'gross_leverage' not in kwargs:
                raise ValueError(
                    'Long/short leveraged portfolio specified for Quant '
                    'Trading System but no gross leverage percentage supplied.'
                )
            gross_leverage = kwargs['gross_leverage']

            qts = QuantTradingSystem(
                self.universe,
                self.broker,
                self.portfolio_id,
                self.data_handler,
                self.alpha_model,
                self.risk_model,
                long_only=self.long_only,
                gross_leverage=gross_leverage,
                submit_orders=True
            )

        return qts

    def _update_equity_curve(self, dt):
        """
        Aggiornamento dei valori della curva equity.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Il tempo in cui sui vuole ottenere l'equity totale del conto.
        """
        self.equity_curve.append(
            (dt, self.broker.get_account_total_equity()["master"])
        )

    def output_holdings(self):
        """
        Invia le posizioni del portafoglio in output.
        """
        self.broker.portfolios[self.portfolio_id].holdings_to_console()

    def get_equity_curve(self):
        """
        Restituisce la curva di equity come Pandas DataFrame.

        Returns
        -------
        `pd.DataFrame`
            La curva equity della strategia indicizzata con data/ora.
        """
        equity_df = pd.DataFrame(
            self.equity_curve, columns=['Date', 'Equity']
        ).set_index('Date')
        equity_df.index = equity_df.index.date
        return equity_df

    def get_target_allocations(self):
        """
        Restituisce le allocazioni target come Pandas DataFrame usanto lo
        stesso indice della curva equity con date di forward-filled.

        Returns
        -------
        `pd.DataFrame`
            Le allocazioni target della strategia indicizzate datetime.
        """
        equity_curve = self.get_equity_curve()
        alloc_df = pd.DataFrame(self.target_allocations).set_index('Date')
        alloc_df.index = alloc_df.index.date
        alloc_df = alloc_df.reindex(index=equity_curve.index, method='ffill')
        if self.burn_in_dt is not None:
            alloc_df = alloc_df[self.burn_in_dt:]
        return alloc_df

    def run(self, results=False):
        """
        Esecuzione il motore di simulazione iterando su tutti gli
        eventi di simulazione, ribilanciando il sistema di trading q
        uantitativo secondo la pianificazione appropriata.

        Parameters
        ----------
        results : `Boolean`, optional
            Se restituire le posizioni correnti del portafoglio.
        """
        if settings.PRINT_EVENTS:
            print("Beginning backtest simulation...")

        stats = {'target_allocations': []}

        for event in self.sim_engine:
            # Output del evento di sistema e timestamp
            dt = event.ts
            if settings.PRINT_EVENTS:
                print("(%s) - %s" % (event.ts, event.event_type))

            # Aggiornamento del broker simulato
            self.broker.update(dt)

            # Aggiornamento di ogni segnale su base giornaliera
            if self.signals is not None and event.event_type == "market_close":
                self.signals.update(dt)

            # Se abbiamo raggiunto un tempo di ribilanciamento, si effettua
            # un'esecuzione completa del sistema di trading quantitativo
            if self._is_rebalance_event(dt):
                if settings.PRINT_EVENTS:
                    print("(%s) - trading logic and rebalance" % event.ts)
                self.qts(dt, stats=stats)

            # Al di fuori dell'orario di mercato, vogliamo un
            # aggiornamento giornaliero delle prestazioni, ma
            # solo se abbiamo superato il periodo di "burn in".
            if event.event_type == "market_close":
                if self.burn_in_dt is not None:
                    if dt >= self.burn_in_dt:
                        self._update_equity_curve(dt)
                else:
                    self._update_equity_curve(dt)

        self.target_allocations = stats['target_allocations']

        # Alla fine della simulazione, se lo si desidera,
        # stampare le posizioni in portafoglio
        if results:
            self.output_holdings()

        if settings.PRINT_EVENTS:
            print("Ending backtest simulation.")
