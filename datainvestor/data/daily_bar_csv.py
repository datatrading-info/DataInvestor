import functools
import os

import numpy as np
import pandas as pd
import pytz
from datainvestor import settings


class CSVDailyBarDataSource(object):
    """
    Encapsulates loading, preparation and querying of CSV files of
    daily 'bar' OHLCV data. The CSV files are converted into a intraday
    timestamped Pandas DataFrame with opening and closing prices.

    Optionally utilises adjusted closing prices (if available) to
    adjust both the close and open.

    Incapsula il caricamento, la preparazione e l'interrogazione di file CSV
    di dati OHLCV "bar" giornalieri. I file CSV sono convertiti in un Pandas
    DataFrame intraday con prezzi di apertura e chiusura.

    Facoltativamente utilizza i prezzi di chiusura rettificati (se disponibili)
    per regolare sia la chiusura che l'apertura.

    Parameters
    ----------
    csv_dir : `str`
        Il percorso completo della directory in cui si trova il CSV.
    asset_type : `str`
        Il tipo di asset a cui si riferiscono i dati sul prezzo/volume.
        TODO: inutilizzato in questa fase e attualmente codificato su Equity.
    adjust_prices : `Boolean`, optional
        Se utilizzare i prezzi rettificati delle azioni aziendali sia per i prezzi
        di apertura che per quelli di chiusura. Il valore predefinito è Vero.
    csv_symbols : `list`, optional
        Un elenco facoltativo di simboli CSV a cui limitare l'origine dati.
        L'alternativa è convertire tutti i CSV trovati nella directory fornita.
    """

    def __init__(self, csv_dir, asset_type, adjust_prices=True, csv_symbols=None):
        self.csv_dir = csv_dir
        self.asset_type = asset_type
        self.adjust_prices = adjust_prices
        self.csv_symbols = csv_symbols

        self.asset_bar_frames = self._load_csvs_into_dfs()
        self.asset_bid_ask_frames = self._convert_bars_into_bid_ask_dfs()

    def _obtain_asset_csv_files(self):
        """
        Ottieni l'elenco di tutti i nomi di file CSV nella directory CSV..

        Returns
        -------
        `list[str]`
            L'elenco di tutti i nomi di file CSV.
        """
        return [
            file for file in os.listdir(self.csv_dir)
            if file.endswith('.csv')
        ]

    def _obtain_asset_symbol_from_filename(self, csv_file):
        """
        Restituisce la simbologia DataInvestor per l'asset.

        TODO: rimuovere l'hardcoding dai tipi di asset Equity.

        Parameters
        ----------
        csv_file : `str`
            Nome del file CSV.

        Returns
        -------
        `str`
            La simbologia DataInvestor dell'asset. es. 'EQ:SPY'.
        """
        return 'EQ:%s' % csv_file.replace('.csv', '')

    def _load_csv_into_df(self, csv_file):
        """
        Carica il file CSV in un Pandas DataFrame con le date
        analizzate, ordinate su datetime localizzate in UTC.

        Parameters
        ----------
        csv_file : `str`
            Nome del file CSV.

        Returns
        -------
        `pd.DataFrame`
            DataFrame del file CSV con timestamp localizzati in UTC.
        """
        csv_df = pd.read_csv(
            os.path.join(self.csv_dir, csv_file),
            index_col='Date',
            parse_dates=True
        ).sort_index()

        # Assicurarsi che tutti i timestamp siano impostati su UTC per coerenza
        csv_df = csv_df.set_index(csv_df.index.tz_localize(pytz.UTC))
        return csv_df

    def _load_csvs_into_dfs(self):
        """
        Carica tutti i CSV nella directory CSV in Pandas DataFrames.

        Returns
        -------
        `dict{pd.DataFrame}`
            Il dizionario con chiave asset-symbol di Pandas DataFrames
            contenente i dati di prezzo/volume con timestamp.
        """
        if settings.PRINT_EVENTS:
            print("Loading CSV files into DataFrames...")
        if self.csv_symbols is not None:
            # TODO/NOTE: Ciò presuppone l'esistenza di simboli CSV
            # all'interno della directory fornita.
            csv_files = ['%s.csv' % symbol for symbol in self.csv_symbols]
        else:
            csv_files = self._obtain_asset_csv_files()

        asset_frames = {}
        for csv_file in csv_files:
            asset_symbol = self._obtain_asset_symbol_from_filename(csv_file)
            if settings.PRINT_EVENTS:
                print("Loading CSV file for symbol '%s'..." % asset_symbol)
            csv_df = self._load_csv_into_df(csv_file)
            asset_frames[asset_symbol] = csv_df
        return asset_frames

    def _convert_bar_frame_into_bid_ask_df(self, bar_df):
        """
        Converte il DataFrame dalle "barre" OHLCV giornaliere in un DataFrame
         di timestamp dei prezzi di apertura e chiusura.

        Facoltativamente, regola i prezzi di apertura/chiusura per le azioni
        utilizzando qualsiasi colonna "Chiusura rettificata" fornita.

        Parameters
        ----------
        `pd.DataFrame`
            Il DataFrame delle barre giornaliere OHLCV.

        Returns
        -------
        `pd.DataFrame`
            I prezzi di apertura/chiusura marcati individualmente,
            opzionalmente adeguati per le azioni.

        """
        bar_df = bar_df.sort_index()
        if self.adjust_prices:
            if 'Adj Close' not in bar_df.columns:
                raise ValueError(
                    "Unable to locate Adjusted Close pricing column in CSV data file. "
                    "Prices cannot be adjusted. Exiting."
                )

            # Limita esclusivamente ai prezzi di apertura/chiusura
            oc_df = bar_df.loc[:, ['Open', 'Close', 'Adj Close']]

            # Aggiuta i prezzi di apertura
            oc_df['Adj Open'] = (oc_df['Adj Close'] / oc_df['Close']) * oc_df['Open']
            oc_df = oc_df.loc[:, ['Adj Open', 'Adj Close']]
            oc_df.columns = ['Open', 'Close']
        else:
            oc_df = bar_df.loc[:, ['Open', 'Close']]

        # Converte le barre in righe separate per i prezzi di
        # apertura/chiusura opportunamente contrassegnati con il timestamp
        seq_oc_df = oc_df.T.unstack(level=0).reset_index()
        seq_oc_df.columns = ['Date', 'Market', 'Price']
        seq_oc_df.loc[seq_oc_df['Market'] == 'Open', 'Date'] += pd.Timedelta(hours=14, minutes=30)
        seq_oc_df.loc[seq_oc_df['Market'] == 'Close', 'Date'] += pd.Timedelta(hours=21, minutes=00)

        # TODO: Impossibile distinguere tra Bid/Ask, implementare in seguito
        dp_df = seq_oc_df[['Date', 'Price']]
        dp_df['Bid'] = dp_df['Price']
        dp_df['Ask'] = dp_df['Price']
        dp_df = dp_df.loc[:, ['Date', 'Bid', 'Ask']].ffill().set_index('Date').sort_index()
        return dp_df

    def _convert_bars_into_bid_ask_dfs(self):
        """
        Convertire tutti i DataFrame giornalieri basati su "barra" OHLCV in
        DataFrame con prezzo di apertura/chiusura con timestamp individuale.

        Returns
        -------
        `dict{pd.DataFrame}`
            Il DataFrames convertito.
        """
        if settings.PRINT_EVENTS:
            print("Adjusting pricing in CSV files...")
        asset_bid_ask_frames = {}
        for asset_symbol, bar_df in self.asset_bar_frames.items():
            if settings.PRINT_EVENTS:
                print("Adjusting CSV file for symbol '%s'..." % asset_symbol)
            asset_bid_ask_frames[asset_symbol] = \
                self._convert_bar_frame_into_bid_ask_df(bar_df)
        return asset_bid_ask_frames

    @functools.lru_cache(maxsize=1024 * 1024)
    def get_bid(self, dt, asset):
        """
        Restituisce il prezzo bid di un asset al timestamp fornito.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Timestamp del prezzo bid da restituire.
        asset : `str`
            Simbolo dell'asset symbol del prezzo bid da restituire.

        Returns
        -------
        `float`
            Il prezzo bid.
        """
        bid_ask_df = self.asset_bid_ask_frames[asset]
        bid_series = bid_ask_df.iloc[bid_ask_df.index.get_indexer([dt], method='pad')]['Bid']
        try:
            bid = bid_series.iloc[0]
        except KeyError:  # Prima della data inizio
            return np.nan
        return bid

    @functools.lru_cache(maxsize=1024 * 1024)
    def get_ask(self, dt, asset):
        """
        Restituisce il prezzo ask di un asset al timestamp fornito.

        Parameters
        ----------
        dt : `pd.Timestamp`
            Timestamp del prezzo ask da restituire.
        asset : `str`
            Simbolo dell'asset symbol del prezzo ask da restituire.

        Returns
        -------
        `float`
            Il prezzo ask.
        """
        bid_ask_df = self.asset_bid_ask_frames[asset]
        ask_series = bid_ask_df.iloc[bid_ask_df.index.get_indexer([dt], method='pad')]['Ask']
        try:
            ask = ask_series.iloc[0]
        except KeyError:  # Prima della data inizio
            return np.nan
        return ask

    def get_assets_historical_closes(self, start_dt, end_dt, assets):
        """
        Restituisce un intervallo storico multi-asset di prezzi di chiusura come
        DataFrame, indicizzato per timestamp con simboli asset come colonne.

        Parameters
        ----------
        start_dt : `pd.Timestamp`
            La data e ora inizio del periodo da restituire
        end_dt : `pd.Timestamp`
            La data e ora fine del periodo da restituire
        assets : `list[str]`
            La lista dei simboli degli asset per i quali restituire i prezzi.

        Returns
        -------
        `pd.DataFrame`
            Dataframe multi-asset dei prezzi di chiusura.
        """
        close_series = []
        for asset in assets:
            if asset in self.asset_bar_frames.keys():
                asset_close_prices = self.asset_bar_frames[asset][['Close']]
                asset_close_prices.columns = [asset]
                close_series.append(asset_close_prices)

        prices_df = pd.concat(close_series, axis=1).dropna(how='all')
        prices_df = prices_df.loc[start_dt:end_dt]
        return prices_df
