import os

import pandas as pd
import pytz

from datainvestor.alpha_model.fixed_signals import FixedSignalsAlphaModel
from datainvestor.asset.equity import Equity
from datainvestor.asset.universe.static import StaticUniverse
from datainvestor.data.backtest_data_handler import BacktestDataHandler
from datainvestor.data.daily_bar_csv import CSVDailyBarDataSource
from datainvestor.statistics.tearsheet import TearsheetStatistics
from datainvestor.trading.backtest import BacktestTradingSession

from datainvestor import settings

if __name__ == "__main__":
    testing = False
    config_file = settings.DEFAULT_CONFIG_FILENAME
    config = settings.from_file(config_file, testing)

    start_dt = pd.Timestamp('2004-11-19 14:30:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2019-12-31 23:59:00', tz=pytz.UTC)

    # Costruisce i simboli e gli asset necessari per il backtest
    strategy_symbols = ['GLD']
    strategy_assets = ['EQ:GLD']
    strategy_universe = StaticUniverse(strategy_assets)

    # Per evitare di caricare tutti i file CSV nella directory,
    # impostare l'origine dati in modo che carichi solo i simboli forniti
    csv_dir = config.CSV_DATA_DIR
    data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=strategy_symbols)
    data_handler = BacktestDataHandler(strategy_universe, data_sources=[data_source])

    # Costruisci un modello Alpha che fornisce semplicemente
    # segnale fisso per il singolo ETF GLD con allocazione del 100%.
    # con un backtest che non ribilancia
    strategy_alpha_model = FixedSignalsAlphaModel({'EQ:GLD': 1.0})
    strategy_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        strategy_universe,
        strategy_alpha_model,
        rebalance='buy_and_hold',
        long_only=True,
        cash_buffer_percentage=0.01,
        data_handler=data_handler
    )
    strategy_backtest.run()

    # Output delle Performance
    tearsheet = TearsheetStatistics(
        strategy_equity=strategy_backtest.get_equity_curve(),
        title='Buy & Hold GLD ETF'
    )
    tearsheet.plot_results()
