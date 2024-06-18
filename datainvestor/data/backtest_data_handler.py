import numpy as np


class BacktestDataHandler(object):
    """
    """

    def __init__(
        self,
        universe,
        data_sources=None
    ):
        self.universe = universe
        self.data_sources = data_sources

    def get_asset_latest_bid_price(self, dt, asset_symbol):
        """
        """
        # TODO: Controllo degli asset nell'universo
        bid = np.nan
        for ds in self.data_sources:
            try:
                bid = ds.get_bid(dt, asset_symbol)
                if not np.isnan(bid):
                    return bid
            except Exception:
                bid = np.nan
        return bid

    def get_asset_latest_ask_price(self, dt, asset_symbol):
        """
        """
        # TODO: Controllo degli asset nell'universo
        ask = np.nan
        for ds in self.data_sources:
            try:
                ask = ds.get_ask(dt, asset_symbol)
                if not np.isnan(ask):
                    return ask
            except Exception:
                ask = np.nan
        return ask

    def get_asset_latest_bid_ask_price(self, dt, asset_symbol):
        """
        """
        # TODO:Per il momento questo è sufficiente per OHLCV
        # dati, che di solito forniscono solo prezzi medi
        # Questo dovrà essere rivisto quando si gestiscono serie temporali bid/ask intraday.
        # È stato aggiunto come meccanismo di ottimizzazione per i backtest interday.
        bid = self.get_asset_latest_bid_price(dt, asset_symbol)
        return (bid, bid)

    def get_asset_latest_mid_price(self, dt, asset_symbol):
        """
        """
        bid_ask = self.get_asset_latest_bid_ask_price(dt, asset_symbol)
        try:
            mid = (bid_ask[0] + bid_ask[1]) / 2.0
        except Exception:
            # TODO: Log
            mid = np.nan
        return mid

    def get_assets_historical_range_close_price(
        self, start_dt, end_dt, asset_symbols, adjusted=False
    ):
        """
        """
        prices_df = None
        for ds in self.data_sources:
            try:
                prices_df = ds.get_assets_historical_closes(
                    start_dt, end_dt, asset_symbols, adjusted=adjusted
                )
                if prices_df is not None:
                    return prices_df
            except Exception:
                raise
        return prices_df
