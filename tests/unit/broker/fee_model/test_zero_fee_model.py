from datainvestor.broker.fee_model.zero_fee_model import ZeroFeeModel


class AssetMock(object):
    def __init__(self):
        pass


class BrokerMock(object):
    def __init__(self):
        pass


def test_commission_is_zero_uniformly():
    """
    Verifica che ogni metodo restituisca zero commissioni,
    indipendentemente dall'asset, dal corrispettivo o dal broker.
    """
    zbc = ZeroFeeModel()
    asset = AssetMock()
    quantity = 100
    consideration = 1000.0
    broker = BrokerMock()

    assert zbc._calc_commission(asset, quantity, consideration, broker=broker) == 0.0
    assert zbc._calc_tax(asset, quantity, consideration, broker=broker) == 0.0
    assert zbc.calc_total_cost(asset, quantity, consideration, broker=broker) == 0.0
