import pytest

from datainvestor.asset.cash import Cash


@pytest.mark.parametrize(
    'currency,expected',
    [
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR')
    ]
)
def test_cash(currency, expected):
    """
    Verifica che l'asset Cash sia istanziato correttamente.
    """
    cash = Cash(currency)

    assert cash.cash_like
    assert cash.currency == expected
