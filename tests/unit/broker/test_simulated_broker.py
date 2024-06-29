import queue

import numpy as np
import pandas as pd
import pytest
import pytz

from datainvestor.broker.portfolio.portfolio import Portfolio
from datainvestor.broker.simulated_broker import SimulatedBroker
from datainvestor.broker.fee_model.zero_fee_model import ZeroFeeModel
from datainvestor import settings


class ExchangeMock(object):
    def get_latest_asset_bid_ask(self, asset):
        return (np.nan, np.nan)

    def is_open_at_datetime(self, dt):
        return True


class ExchangeMockException(object):
    def get_latest_asset_bid_ask(self, asset):
        raise ValueError("No price available!")

    def is_open_at_datetime(self, dt):
        return True


class ExchangeMockPrice(object):
    def is_open_at_datetime(self, dt):
        return True


class DataHandlerMock(object):
    def get_asset_latest_bid_ask_price(self, dt, asset):
        return (np.nan, np.nan)

    def get_asset_latest_mid_price(self, dt, asset):
        return np.nan


class DataHandlerMockPrice(object):
    def get_asset_latest_bid_ask_price(self, dt, asset):
        return (53.45, 53.47)

    def get_asset_latest_mid_price(self, dt, asset):
        return (53.47 - 53.45) / 2.0


class OrderMock(object):
    def __init__(self, asset, quantity, order_id=None):
        self.asset = asset
        self.quantity = quantity
        self.order_id = 1 if order_id is None else order_id
        self.direction = np.copysign(1, self.quantity)


class AssetMock(object):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol


def test_initial_settings_for_default_simulated_broker():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Test a default SimulatedBroker
    sb1 = SimulatedBroker(start_dt, exchange, data_handler)

    assert sb1.start_dt == start_dt
    assert sb1.current_dt == start_dt
    assert sb1.exchange == exchange
    assert sb1.account_id is None
    assert sb1.base_currency == "USD"
    assert sb1.initial_funds == 0.0
    assert type(sb1.fee_model) == ZeroFeeModel

    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )

    assert sb1.cash_balances == tcb1
    assert sb1.portfolios == {}
    assert sb1.open_orders == {}

    # Test a SimulatedBroker with some parameters set
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, account_id="ACCT1234",
        base_currency="GBP", initial_funds=1e6,
        fee_model=ZeroFeeModel()
    )

    assert sb2.start_dt == start_dt
    assert sb2.current_dt == start_dt
    assert sb2.exchange == exchange
    assert sb2.account_id == "ACCT1234"
    assert sb2.base_currency == "GBP"
    assert sb2.initial_funds == 1e6
    assert type(sb2.fee_model) == ZeroFeeModel

    tcb2 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb2["GBP"] = 1e6

    assert sb2.cash_balances == tcb2
    assert sb2.portfolios == {}
    assert sb2.open_orders == {}


def test_bad_set_base_currency():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    with pytest.raises(ValueError):
        SimulatedBroker(
            start_dt, exchange, data_handler, base_currency="XYZ"
        )


def test_good_set_base_currency():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(
        start_dt, exchange, data_handler, base_currency="EUR"
    )
    assert sb.base_currency == "EUR"


def test_bad_set_initial_funds():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    with pytest.raises(ValueError):
        SimulatedBroker(
            start_dt, exchange, data_handler, initial_funds=-56.34
        )


def test_good_set_initial_funds():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler, initial_funds=1e4)
    assert sb._set_initial_funds(1e4) == 1e4


def test_all_cases_of_set_broker_commission():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Broker commission is None
    sb1 = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb1.fee_model.__class__.__name__ == "ZeroFeeModel"

    # Broker commission is specified as a subclass
    # of FeeModel abstract base class
    bc2 = ZeroFeeModel()
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, fee_model=bc2
    )
    assert sb2.fee_model.__class__.__name__ == "ZeroFeeModel"

    # FeeModel is mis-specified and thus
    # raises a TypeError
    with pytest.raises(TypeError):
        SimulatedBroker(
            start_dt, exchange, data_handler, fee_model="bad_fee_model"
        )


def test_set_cash_balances():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    # Zero initial funds
    sb1 = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=0.0
    )
    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    assert sb1._set_cash_balances() == tcb1

    # Non-zero initial funds
    sb2 = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=12345.0
    )
    tcb2 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb2["USD"] = 12345.0
    assert sb2._set_cash_balances() == tcb2


def test_set_initial_portfolios():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb._set_initial_portfolios() == {}


def test_set_initial_open_orders():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    assert sb._set_initial_open_orders() == {}


def test_subscribe_funds_to_account():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_account(-4306.23)

    # Correctly setting cash_balances for a positive amount
    sb.subscribe_funds_to_account(165303.23)
    assert sb.cash_balances[sb.base_currency] == 165303.23


def test_withdraw_funds_from_account():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler, initial_funds=1e6)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_account(-4306.23)

    # Raising ValueError for lack of cash
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_account(2e6)

    # Correctly setting cash_balances for a positive amount
    sb.withdraw_funds_from_account(3e5)
    assert sb.cash_balances[sb.base_currency] == 7e5


def test_get_account_cash_balance():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(
        start_dt, exchange, data_handler, initial_funds=1000.0
    )

    # If currency is None, return the cash balances
    sbcb1 = sb.get_account_cash_balance()
    tcb1 = dict(
        zip(
            settings.SUPPORTED['CURRENCIES'],
            [0.0] * len(settings.SUPPORTED['CURRENCIES'])
        )
    )
    tcb1["USD"] = 1000.0
    assert sbcb1 == tcb1

    # If the currency code isn't in the cash_balances
    # dictionary, then raise ValueError
    with pytest.raises(ValueError):
        sb.get_account_cash_balance(currency="XYZ")

    # Otherwise, return appropriate cash balance
    assert sb.get_account_cash_balance(currency="USD") == 1000.0
    assert sb.get_account_cash_balance(currency="EUR") == 0.0


def test_get_account_total_market_value():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Subscribe all necessary funds and create portfolios
    sb.subscribe_funds_to_account(300000.0)
    sb.create_portfolio(portfolio_id="1", name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="2", name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="3", name="My Portfolio #1")
    sb.subscribe_funds_to_portfolio("1", 100000.0)
    sb.subscribe_funds_to_portfolio("2", 100000.0)
    sb.subscribe_funds_to_portfolio("3", 100000.0)

    # Check that the market value is correct
    res_equity = sb.get_account_total_equity()
    test_equity = {
        "1": 100000.0,
        "2": 100000.0,
        "3": 100000.0,
        "master": 300000.0
    }
    assert res_equity == test_equity


def test_create_portfolio():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # If portfolio_id isn't in the dictionary, then check it
    # was created correctly, along with the orders dictionary
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio")
    assert "1234" in sb.portfolios
    assert isinstance(sb.portfolios["1234"], Portfolio)
    assert "1234" in sb.open_orders
    assert isinstance(sb.open_orders["1234"], queue.Queue)

    # If portfolio is already in the dictionary
    # then raise ValueError
    with pytest.raises(ValueError):
        sb.create_portfolio(
            portfolio_id=1234, name="My Portfolio"
        )


def test_list_all_portfolio():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # If empty portfolio dictionary, return empty list
    assert sb.list_all_portfolios() == []

    # If non-empty, return sorted list via the portfolio IDs
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.create_portfolio(portfolio_id="z154", name="My Portfolio #2")
    sb.create_portfolio(portfolio_id="abcd", name="My Portfolio #3")

    res_ports = sorted([
        p.portfolio_id
        for p in sb.list_all_portfolios()
    ])
    test_ports = ["1234", "abcd", "z154"]
    assert res_ports == test_ports


def test_subscribe_funds_to_portfolio():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_portfolio("1234", -4306.23)

    # Raising KeyError if portfolio doesn't exist
    with pytest.raises(KeyError):
        sb.subscribe_funds_to_portfolio("1234", 5432.12)

    # Add in cash balance to the account
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(165303.23)

    # Raising ValueError if not enough cash
    with pytest.raises(ValueError):
        sb.subscribe_funds_to_portfolio("1234", 200000.00)

    # If everything else worked, check balances are correct
    sb.subscribe_funds_to_portfolio("1234", 100000.00)
    assert sb.cash_balances[sb.base_currency] == 65303.23000000001
    assert sb.portfolios["1234"].cash == 100000.00


def test_withdraw_funds_from_portfolio():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError with negative amount
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_portfolio("1234", -4306.23)

    # Raising KeyError if portfolio doesn't exist
    with pytest.raises(KeyError):
        sb.withdraw_funds_from_portfolio("1234", 5432.12)

    # Add in cash balance to the account
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(165303.23)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Raising ValueError if not enough cash
    with pytest.raises(ValueError):
        sb.withdraw_funds_from_portfolio("1234", 200000.00)

    # If everything else worked, check balances are correct
    sb.withdraw_funds_from_portfolio("1234", 50000.00)
    assert sb.cash_balances[sb.base_currency] == 115303.23000000001
    assert sb.portfolios["1234"].cash == 50000.00


def test_get_portfolio_cash_balance():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising ValueError if portfolio_id not in keys
    with pytest.raises(ValueError):
        sb.get_portfolio_cash_balance("5678")

    # Create fund transfers and portfolio
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(175000.0)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Check correct values obtained after cash transfers
    assert sb.get_portfolio_cash_balance("1234") == 100000.0


def test_get_portfolio_total_market_value():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)

    # Raising KeyError if portfolio_id not in keys
    with pytest.raises(KeyError):
        sb.get_portfolio_total_market_value("5678")

    # Create fund transfers and portfolio
    sb.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sb.subscribe_funds_to_account(175000.0)
    sb.subscribe_funds_to_portfolio("1234", 100000.00)

    # Check correct values obtained after cash transfers
    assert sb.get_portfolio_total_equity("1234") == 100000.0


def test_submit_order():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)

    # Raising KeyError if portfolio_id not in keys
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    asset = 'EQ:RDSB'
    quantity = 100
    order = OrderMock(asset, quantity)
    with pytest.raises(KeyError):
        sb.submit_order("1234", order)

    # Raises ValueError if bid/ask is (np.nan, np.nan)
    exchange_exception = ExchangeMockException()
    sbnp = SimulatedBroker(start_dt, exchange_exception, data_handler)
    sbnp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    quantity = 100
    order = OrderMock(asset, quantity)
    with pytest.raises(ValueError):
        sbnp._execute_order(start_dt, "1234", order)

    # Checks that bid/ask are correctly set dependent on
    # order direction

    # Positive direction
    exchange_price = ExchangeMockPrice()
    data_handler_price = DataHandlerMockPrice()

    sbwp = SimulatedBroker(start_dt, exchange_price, data_handler_price)
    sbwp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sbwp.subscribe_funds_to_account(175000.0)
    sbwp.subscribe_funds_to_portfolio("1234", 100000.00)
    quantity = 1000
    order = OrderMock(asset, quantity)
    sbwp.submit_order("1234", order)
    sbwp.update(start_dt)

    port = sbwp.portfolios["1234"]
    assert port.cash == 46530.0
    assert port.total_market_value == 53470.0
    assert port.total_equity == 100000.0
    assert port.pos_handler.positions[asset].unrealised_pnl == 0.0
    assert port.pos_handler.positions[asset].market_value == 53470.0
    assert port.pos_handler.positions[asset].net_quantity == 1000

    # Negative direction
    exchange_price = ExchangeMockPrice()
    sbwp = SimulatedBroker(start_dt, exchange_price, data_handler_price)
    sbwp.create_portfolio(portfolio_id=1234, name="My Portfolio #1")
    sbwp.subscribe_funds_to_account(175000.0)
    sbwp.subscribe_funds_to_portfolio("1234", 100000.00)
    quantity = -1000
    order = OrderMock(asset, quantity)
    sbwp.submit_order("1234", order)
    sbwp.update(start_dt)

    port = sbwp.portfolios["1234"]
    assert port.cash == 153450.0
    assert port.total_market_value == -53450.0
    assert port.total_equity == 100000.0
    assert port.pos_handler.positions[asset].unrealised_pnl == 0.0
    assert port.pos_handler.positions[asset].market_value == -53450.0
    assert port.pos_handler.positions[asset].net_quantity == -1000


def test_update_sets_correct_time():
    """
    """
    start_dt = pd.Timestamp('2017-10-05 08:00:00', tz=pytz.UTC)
    new_dt = pd.Timestamp('2017-10-07 08:00:00', tz=pytz.UTC)
    exchange = ExchangeMock()
    data_handler = DataHandlerMock()

    sb = SimulatedBroker(start_dt, exchange, data_handler)
    sb.update(new_dt)
    assert sb.current_dt == new_dt
