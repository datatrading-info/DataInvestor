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

    start_dt = pd.Timestamp('2007-01-31 14:30:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2020-05-31 23:59:00', tz=pytz.UTC)

    # Costruisce i simboli e gli asset necessari per il backtest
    strategy_symbols = ['TLT', 'IEI']
    strategy_assets = ['EQ:%s' % symbol for symbol in strategy_symbols]
    strategy_universe = StaticUniverse(strategy_assets)

    # Per evitare di caricare tutti i file CSV nella directory,
    # impostare l'origine dati in modo che carichi solo i simboli forniti
    csv_dir = config.CSV_DATA_DIR
    data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=strategy_symbols)
    data_handler = BacktestDataHandler(strategy_universe, data_sources=[data_source])

    # Costruisce un modello Alpha che fornisce semplicemente
    # allocazioni statiche a un universo di asset
    # In questo caso 100% TLT ETF, -70% IEI ETF,
    # ribilanciato alla fine di ogni mese, con leva 5x
    strategy_alpha_model = FixedSignalsAlphaModel(
        {'EQ:TLT': 1.0, 'EQ:IEI': -0.7}
    )
    strategy_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        strategy_universe,
        strategy_alpha_model,
        rebalance='end_of_month',
        long_only=False,
        gross_leverage=5.0,
        data_handler=data_handler
    )
    strategy_backtest.run()

    # Costruisce gli asset di benchmark (buy & hold SPY)
    benchmark_symbols = ['SPY']
    benchmark_assets = ['EQ:SPY']
    benchmark_universe = StaticUniverse(benchmark_assets)
    benchmark_data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=benchmark_symbols)
    benchmark_data_handler = BacktestDataHandler(benchmark_universe, data_sources=[benchmark_data_source])

    # Costruisce un modello Alpha di riferimento che fornisce
    # un'allocazione statica al 100% all'ETF SPY, senza ribilanciamento
    benchmark_alpha_model = FixedSignalsAlphaModel({'EQ:SPY': 1.0})
    benchmark_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        benchmark_universe,
        benchmark_alpha_model,
        rebalance='buy_and_hold',
        long_only=True,
        cash_buffer_percentage=0.01,
        data_handler=benchmark_data_handler
    )
    benchmark_backtest.run()

    # Output delle Performance
    tearsheet = TearsheetStatistics(
        strategy_equity=strategy_backtest.get_equity_curve(),
        benchmark_equity=benchmark_backtest.get_equity_curve(),
        title='Long/Short Leveraged Treasury Bond ETFs'
    )
    tearsheet.plot_results()
