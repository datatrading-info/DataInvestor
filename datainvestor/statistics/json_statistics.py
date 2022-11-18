import datetime
import json

import pandas as pd
import numpy as np

from datainvestor import settings
import datainvestor.statistics.performance as perf


class JSONStatistics(object):
    """
    Classe autonoma per l'output delle statistiche di backtest
    di base in un formato di file JSON.

    Parameters
    ----------
    equity_curve : `pd.DataFrame`
        Il DataFrame della curva equity indicizzata per data-ora.
    strategy_id : `str`, optional
        La stringa ID per la strategia da passare al dict delle statistiche.
    strategy_name : `str`, optional
        La stringa del nome per la strategia da passare al dict delle statistiche.
    benchmark_curve : `pd.DataFrame`, optional
        Il Dataframe dell'equity curve per il benchmark indicizzato per tempo.
    benchmark_id : `str`, optional
        La stringa ID per il benchmark da passare al dict delle statistiche.
    benchmark_name : `str`, optional
        La stringa del nome per il benchmark da passare al dict delle statistiche.
    periods : `int`, optional
        Il numero di periodi da utilizzare per il calcolo dell'indice di Sharpe.
    output_filename : `str`
        Il nome del file di output per il dizionario delle statistiche JSON.
    """

    def __init__(
        self,
        equity_curve,
        target_allocations,
        strategy_id=None,
        strategy_name=None,
        benchmark_curve=None,
        benchmark_id=None,
        benchmark_name=None,
        periods=252,
        output_filename='statistics'
    ):
        self.equity_curve = equity_curve
        self.target_allocations = target_allocations
        self.strategy_id = strategy_id
        self.strategy_name = strategy_name
        self.benchmark_curve = benchmark_curve
        self.benchmark_id = benchmark_id
        self.benchmark_name = benchmark_name
        self.periods = periods
        self.output_filename = output_filename
        self.statistics = self._create_full_statistics()

    @staticmethod
    def _series_to_tuple_list(series):
        """
        Converte le serie Panda indicizzate per data e ora in un
        elenco di tuple indicizzate per millisecondi dall'epoca.

        Parameters
        ----------
        series : `pd.Series`
            La Serie Pandas da convertire.

        Returns
        -------
        `list[tuple]`
            L'elenco dei valori di tupla con indicizzazione di epoche.
        """
        return [
            (
                int(
                    datetime.datetime.combine(
                        k, datetime.datetime.min.time()
                    ).timestamp() * 1000.0
                ), v if not np.isnan(v) else 0.0
            )
            for k, v in series.to_dict().items()
        ]

    @staticmethod
    def _dataframe_to_column_list(df):
        """
        Converte Pandas DataFrame indicizzato per data e ora in un
        elenco di tuple indicizzate per millisecondi dall'epoca.

        Parameters
        ----------
        df : `pd.DataFrame`
            Il DataFrame da convertire.

        Returns
        -------
        `list[tuple]`
            L'elenco dei valori di tupla con indicizzazione di epoche.
        """
        col_list = []
        for k, v in df.to_dict().items():
            name = k.replace('EQ:', '')
            date_val_tups = [
                (
                    int(
                        datetime.datetime.combine(
                            date_key, datetime.datetime.min.time()
                        ).timestamp() * 1000.0
                    ), date_val if not np.isnan(date_val) else 0.0
                )
                for date_key, date_val in v.items()
            ]
            col_list.append({'name': name, 'data': date_val_tups})
        return col_list

    @staticmethod
    def _calculate_returns(curve):
        """
        Aggiunge i rendimenti e i rendimenti cumulativi nel Dataframe della curva di equity.

        Parameters
        ----------
        curve : `pd.DataFrame`
            Il DataFrame della curva equity
        """
        curve['Returns'] = curve['Equity'].pct_change().fillna(0.0)
        curve['CumReturns'] = np.exp(np.log(1 + curve['Returns']).cumsum())

    def _calculate_monthly_aggregated_returns(self, returns):
        """
        Calcola i rendimenti aggregati mensili come un elenco di tuple, con la
        prima voce un'ulteriore tupla di (anno, mese) e la seconda voce i
        rendimenti. 0% -> 0,0, 100% -> 1,0

        Parameters
        ----------
        returns : `pd.Series`
            La Serie di valori di rendimento giornalieri.

        Returns
        -------
        `list[tuple]`
            L'elenco dei rendimenti basati su tuple: [((year, month), return)]
        """
        month_returns = perf.aggregate_returns(returns, 'monthly')
        return list(zip(month_returns.index, month_returns))

    def _calculate_monthly_aggregated_returns_hc(self, returns):
        """
        Calcola i rendimenti aggregati mensili nel formato utilizzato
        da Highcharts. 0% -> 0,0, 100% -> 100,0

        Parameters
        ----------
        returns : `pd.Series`
            La Serie di valori di rendimento giornalieri.

        Returns
        -------
        `list[tuple]`
            L'elenco dei rendimenti basati su tuple: [((year, month), return)]
        """
        month_returns = perf.aggregate_returns(returns, 'monthly')

        data = []

        years = month_returns.index.levels[0].tolist()
        years_range = range(0, len(years))
        months_range = range(0, 12)

        for month in months_range:
            for year in years_range:
                try:
                    data.append([month, year, 100.0 * month_returns.loc[(years[year], month + 1)]])
                except KeyError:  # Anno troncato, quindi nessun dato disponibile
                    pass

        return data

    def _calculate_yearly_aggregated_returns(self, returns):
        """
        Calcola i rendimenti aggregati annuali come un elenco di tuple,
        con la prima voce che è l'intero anno e la seconda voce i
        rendimenti. 0% -> 0,0, 100% -> 1,0

        Parameters
        ----------
        returns : `pd.Series`
            La Serie dei valori dei rendimenti giornalieri.

        Returns
        -------
        `list[tuple]`
            L'elenco dei rendimenti basati su tuple: [(year, return)]
        """
        year_returns = perf.aggregate_returns(returns, 'yearly')
        return list(zip(year_returns.index, year_returns))

    def _calculate_yearly_aggregated_returns_hc(self, returns):
        """
        Calcola i rendimenti aggregati annuali nel formato
        utilizzato da Highcharts. 0% -> 0,0, 100% -> 100,0

        Parameters
        ----------
        returns : `list[tuple]`
            L'elenco delle tuple, con il primo indice come intero
            anno e il secondo indice come rendimento.

        Returns
        -------
        `list[float]`
            La lista dei rendimenti.
        """
        year_returns = self._calculate_yearly_aggregated_returns(returns)
        return [year[1] * 100.0 for year in year_returns]

    def _calculate_returns_quantiles_dict(self, returns):
        """
        Crea un dizionario con i quantili per le serie dei rendimenti fornite.

        Parameters
        ----------
        returns : `pd.Series` or `list[float]`
            La Serie/elenco dei valori dei rendimenti.

        Returns
        -------
        `dict{str: float}`
            I quantili delle serie dei rendimenti forniti.
        """
        return {
            'min': np.min(returns),
            'lq': np.percentile(returns, 25),
            'med': np.median(returns),
            'uq': np.percentile(returns, 75),
            'max': np.max(returns)
        }

    def _calculate_returns_quantiles(self, daily_returns):
        """
        Crea un dict-of-dicts con quantili per le serie di
        rendimenti giornalieri, mensili e annuali.

        Parameters
        ----------
        daily_returns : `pd.Series`
            La Serie dei valori di rendimento giornalieri.

        Returns
        -------
        `dict{str: dict{str: float}}`
            I quantili dei rendimenti giornalieri, mensili e annuali.
        """
        monthly_returns = [m[1] for m in self._calculate_monthly_aggregated_returns(daily_returns)]
        yearly_returns = [y[1] for y in self._calculate_yearly_aggregated_returns(daily_returns)]
        return {
            'daily': self._calculate_returns_quantiles_dict(daily_returns),
            'monthly': self._calculate_returns_quantiles_dict(monthly_returns),
            'yearly': self._calculate_returns_quantiles_dict(yearly_returns)
        }

    def _calculate_returns_quantiles_hc(self, returns_quantiles):
        """
        Converte i dict-of-dicts dei quantili dei rendimenti in un formato
        adatto per boxplot Highcharts.

        Parameters
        ----------
        `dict{str: dict{str: float}}`
            I quantili dei rendimenti giornalieri, mensili e annuali.

        Returns
        -------
        `list[list[float]]`
            La list-of-lists dei quantili dei rendimenti (in termini percentuali 0-100).
        """
        percentiles = ['min', 'lq', 'med', 'uq', 'max']
        return [
            [returns_quantiles['daily'][stat] * 100.0 for stat in percentiles],
            [returns_quantiles['monthly'][stat] * 100.0 for stat in percentiles],
            [returns_quantiles['yearly'][stat] * 100.0 for stat in percentiles]
        ]

    def _calculate_statistics(self, curve):
        """
        Crea un dizionario di varie statistiche associate al backtest di una
        strategia di trading tramite una curva equity fornita.

        Tutte le serie Panda indicizzate per data e ora vengono convertite in
        millisecondi dalla rappresentazione dell'epoca.

        Parameters
        ----------
        curve : `pd.DataFrame`
            Il DataFrame della curva di equity.

        Returns
        -------
        `dict`
            Il dizionario delle statistiche.
        """
        stats = {}

        # Drawdown, max drawdown, durata del max drawdown
        dd_s, max_dd, dd_dur = perf.create_drawdowns(curve['CumReturns'])

        # Curva equity e rendimenti
        stats['equity_curve'] = JSONStatistics._series_to_tuple_list(curve['Equity'])
        stats['returns'] = JSONStatistics._series_to_tuple_list(curve['Returns'])
        stats['cum_returns'] = JSONStatistics._series_to_tuple_list(curve['CumReturns'])

        # Rendimenti aggregati mese/anno
        stats['monthly_agg_returns'] = self._calculate_monthly_aggregated_returns(curve['Returns'])
        stats['monthly_agg_returns_hc'] = self._calculate_monthly_aggregated_returns_hc(curve['Returns'])
        stats['yearly_agg_returns'] = self._calculate_yearly_aggregated_returns(curve['Returns'])
        stats['yearly_agg_returns_hc'] = self._calculate_yearly_aggregated_returns_hc(curve['Returns'])

        # quantili dei rendimenti
        stats['returns_quantiles'] = self._calculate_returns_quantiles(curve['Returns'])
        stats['returns_quantiles_hc'] = self._calculate_returns_quantiles_hc(stats['returns_quantiles'])

        # Statistiche dei Drawdown
        stats['drawdowns'] = JSONStatistics._series_to_tuple_list(dd_s)
        stats['max_drawdown'] = max_dd
        stats['max_drawdown_duration'] = dd_dur

        # Performance
        stats['mean_returns'] = np.mean(curve['Returns'])
        stats['stdev_returns'] = np.std(curve['Returns'])
        stats['cagr'] = perf.create_cagr(curve['CumReturns'], self.periods)
        stats['annualised_vol'] = np.std(curve['Returns']) * np.sqrt(self.periods)
        stats['sharpe'] = perf.create_sharpe_ratio(curve['Returns'], self.periods)
        stats['sortino'] = perf.create_sortino_ratio(curve['Returns'], self.periods)

        return stats

    def _calculate_allocations(self, allocations):
        """
        """
        return JSONStatistics._dataframe_to_column_list(allocations)

    def _create_full_statistics(self):
        """
        Crea il dizionario delle statistiche "completo", che contiene una voce
        per la strategia e una voce facoltativa per qualsiasi benchmark fornito.

        Returns
        -------
        `dict`
            Il dizionario delle statistiche della strategia e del benchmark (facoltativo).
        """
        full_stats = {}

        JSONStatistics._calculate_returns(self.equity_curve)
        full_stats['strategy'] = self._calculate_statistics(self.equity_curve)
        full_stats['strategy']['target_allocations'] = self._calculate_allocations(
            self.target_allocations
        )

        if self.benchmark_curve is not None:
            JSONStatistics._calculate_returns(self.benchmark_curve)
            full_stats['benchmark'] = self._calculate_statistics(self.benchmark_curve)

        if self.strategy_id is not None:
            full_stats['strategy_id'] = self.strategy_id
        if self.strategy_name is not None:
            full_stats['strategy_name'] = self.strategy_name
        if self.benchmark_id is not None:
            full_stats['benchmark_id'] = self.benchmark_id
        if self.benchmark_name is not None:
            full_stats['benchmark_name'] = self.benchmark_name

        return full_stats

    def to_file(self):
        """
        Scrive il dizionario delle statistiche in un file JSON.
        """
        if settings.PRINT_EVENTS:
            print('Outputting JSON results to "%s"...' % self.output_filename)
        with open(self.output_filename + '.json', 'w') as outfile:
            json.dump(self.statistics, outfile)
