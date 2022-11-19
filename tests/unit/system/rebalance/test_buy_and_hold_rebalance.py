import pandas as pd
import pytest
import pytz

from datainvestor.system.rebalance.buy_and_hold import BuyAndHoldRebalance


@pytest.mark.parametrize(
    "start_dt", [('2020-01-01'), ('2020-02-02')]
)
def test_buy_and_hold_rebalance(start_dt):
    """
    """
    sd = pd.Timestamp(start_dt, tz=pytz.UTC)
    reb = BuyAndHoldRebalance(start_dt=sd)

    assert reb.start_dt == sd
    assert reb.rebalances == [sd]
