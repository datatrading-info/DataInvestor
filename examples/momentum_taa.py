import operator
import os

import pandas as pd
import pytz

from datainvestor.alpha_model.alpha_model import AlphaModel
from datainvestor.alpha_model.fixed_signals import FixedSignalsAlphaModel
from datainvestor.asset.equity import Equity
from datainvestor.asset.universe.dynamic import DynamicUniverse
from datainvestor.asset.universe.static import StaticUniverse
from datainvestor.signals.momentum import MomentumSignal
from datainvestor.signals.signals_collection import SignalsCollection
from datainvestor.data.backtest_data_handler import BacktestDataHandler
from datainvestor.data.daily_bar_csv import CSVDailyBarDataSource
from datainvestor.statistics.tearsheet import TearsheetStatistics
from datainvestor.trading.backtest import BacktestTradingSession
from datainvestor import settings

class TopNMomentumAlphaModel(AlphaModel):

    def __init__(
            self, signals, mom_lookback, mom_top_n, universe, data_handler
    ):
        """
        Inizializzazione del TopNMomentumAlphaModel

        Parameters
        ----------
        signals : `SignalsCollection`
            L'entità per l'interfacciamento con vari segnali
            precalcolati. In questo caso vogliamo usare 'momentum'.
        mom_lookback : `integer`
            Il numero di giorni lavorativi su cui calcolare
            il momentum lookback.
        mom_top_n : `integer`
            Il numero di asset da includere nel portafoglio,
            in ordine discendente dal momentum più alto.
        universe : `Universe`
            L'insieme di asset utilizzati per la generazione dei signali.
        data_handler : `DataHandler`
            L'interfaccia per i dati CSV.

        Returns
        -------
        None
        """
        self.signals = signals
        self.mom_lookback = mom_lookback
        self.mom_top_n = mom_top_n
        self.universe = universe
        self.data_handler = data_handler

    def _highest_momentum_asset(
            self, dt
    ):
        """
        Calcola l'elenco ordinato degli asset con momentum più performanti
        limitati ai "Top N", per una determinata data e ora.

        Parameters
        ----------
        dt : `pd.Timestamp`
            La data e l'ora per la quale devono essere calcolati
            gli asset con momentum più elevato.

        Returns
        -------
        `list[str]`
            Elenco ordinato degli asset con momentum più
            performante limitato ai "Top N".
        """
        assets = self.signals['momentum'].assets

        # Calcola il momentum dei rendimento del periodo di holding per ciascun
        # asset, per il periodo di ricerca di momentum specificato.
        all_momenta = {
            asset: self.signals['momentum'](
                asset, self.mom_lookback
            ) for asset in assets
        }

        # Calcolo dell'elenco degli asset con le migliori prestazioni
        # in base al momentum, limitato dal numero di asset desiderate
        # da negoziare ogni mese
        return [
                asset[0] for asset in sorted(
                    all_momenta.items(),
                    key=operator.itemgetter(1),
                    reverse=True
                )
               ][:self.mom_top_n]

    def _generate_signals(
            self, dt, weights
    ):
        """
        Calcola il momentum più performante per ciascun asset,
        quindi assegna 1/N del peso del segnale a ciascuno
        di questi asset.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Data/ora per la quale devono essere calcolati
            i pesi del segnale.
        weights : `dict{str: float}`
            Il dizionario dei pesi dei segnali.

        Returns
        -------
        `dict{str: float}`
            Il dizionario dei pesi dei segnali appena creato.
        """
        top_assets = self._highest_momentum_asset(dt)
        for asset in top_assets:
            weights[asset] = 1.0 / self.mom_top_n
        return weights

    def __call__(
            self, dt
    ):
        """
        Calculates the signal weights for the top N
        momentum alpha model, assuming that there is
        sufficient data to begin calculating momentum
        on  e desired assets.
        Calcola i pesi del segnale per il modello alfa dei top N momentum,
        presupponendo che vi siano dati sufficienti per iniziare a
        calcolare il momentum per gli asset desiderati.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Data/ora per la quale devono essere calcolati
            i pesi del segnale.

        Returns
        -------
        `dict{str: float}`
            Il dizionario dei pesi dei segnali appena creato.
        """
        assets = self.universe.get_assets(dt)
        weights = {asset: 0.0 for asset in assets}

        # Genera pesi solo se l'ora corrente supera
        # il periodo di lookback del momentum
        if self.signals.warmup >= self.mom_lookback:
            weights = self._generate_signals(dt, weights)
        return weights


if __name__ == "__main__":
    testing = False
    config_file = settings.DEFAULT_CONFIG_FILENAME
    config = settings.from_file(config_file, testing)

    # Durata del backtest
    start_dt = pd.Timestamp('1998-12-22 14:30:00', tz=pytz.UTC)
    burn_in_dt = pd.Timestamp('1999-12-22 14:30:00', tz=pytz.UTC)
    end_dt = pd.Timestamp('2020-12-31 23:59:00', tz=pytz.UTC)

    # Parametri del modello
    mom_lookback = 126  # Sei mesi di giorni di mercato aperto
    mom_top_n = 3  # Numero di asset da includere ad ogni ribilanciamento

    # Costruzione dei simboli e degli asset necessari per il backtest. Si usa gli ETF
    # settoriali SPDR del mercato statunitense, tutti quelli che iniziato per XL
    strategy_symbols = ['XL%s' % sector for sector in "BCEFIKPUVY"]
    assets = ['EQ:%s' % symbol for symbol in strategy_symbols]

    # Poiché si tratta di un universo dinamico di asset (XLC viene aggiunto in seguito),
    # dobbiamo comunicare a DataInvestor quando XLC può essere incluso. A tale scopo si usa
    # un dizionario delle date degli asset
    asset_dates = {asset: start_dt for asset in assets}
    asset_dates['EQ:XLC'] = pd.Timestamp('2018-06-18 00:00:00', tz=pytz.UTC)
    strategy_universe = DynamicUniverse(asset_dates)

    # Per evitare di caricare tutti i file CSV nella directory,
    # impostiamo l'origine dati in modo che carichiamo solo i simboli forniti
    csv_dir = config.CSV_DATA_DIR
    strategy_data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=strategy_symbols)
    strategy_data_handler = BacktestDataHandler(strategy_universe, data_sources=[strategy_data_source])

    # Genera i segnali (in questo caso il momentum basato sul rendimento
    # del periodo di holding) usati nel modello alfa del momentum top-N
    momentum = MomentumSignal(start_dt, strategy_universe, lookbacks=[mom_lookback])
    signals = SignalsCollection({'momentum': momentum}, strategy_data_handler)

    # Genera l'istanza del modello alfa per il modello alfa del momentum top-N
    strategy_alpha_model = TopNMomentumAlphaModel(
        signals, mom_lookback, mom_top_n, strategy_universe, strategy_data_handler
    )

    # Costruzione del backtest della strategia e l'esegue
    strategy_backtest = BacktestTradingSession(
        start_dt,
        end_dt,
        strategy_universe,
        strategy_alpha_model,
        signals=signals,
        rebalance='end_of_month',
        long_only=True,
        cash_buffer_percentage=0.01,
        burn_in_dt=burn_in_dt,
        data_handler=strategy_data_handler
    )
    strategy_backtest.run()

    # Costruzione degli asset del benchmark (buy & hold SPY)
    benchmark_symbols = ['SPY']
    benchmark_assets = ['EQ:SPY']
    benchmark_universe = StaticUniverse(benchmark_assets)
    benchmark_data_source = CSVDailyBarDataSource(csv_dir, Equity, csv_symbols=benchmark_symbols)
    benchmark_data_handler = BacktestDataHandler(benchmark_universe, data_sources=[benchmark_data_source])

    # Costruzione di un modello Alpha di benchmark che fornisca un'allocazione
    # statica al 100% all'ETF SPY, senza ribilanciamento
    benchmark_alpha_model = FixedSignalsAlphaModel({'EQ:SPY': 1.0})
    benchmark_backtest = BacktestTradingSession(
        burn_in_dt,
        end_dt,
        benchmark_universe,
        benchmark_alpha_model,
        rebalance='buy_and_hold',
        long_only=True,
        cash_buffer_percentage=0.01,
        data_handler=benchmark_data_handler
    )
    benchmark_backtest.run()

    # Output delle performance
    tearsheet = TearsheetStatistics(
        strategy_equity=strategy_backtest.get_equity_curve(),
        benchmark_equity=benchmark_backtest.get_equity_curve(),
        title='US Sector Momentum - Top 3 Sectors'
    )
    tearsheet.plot_results()