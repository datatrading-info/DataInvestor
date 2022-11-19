import pytest


class Helpers:
    @staticmethod
    def assert_order_lists_equal(orders_1, orders_2):
        """
        Esegue il confronto in base all'ordine su tutti gli attributi dell'ordine
        ad eccezione dell'ID generato, al fine di determinare
        se due liste di ordini sono uguali.

        Parametri
        ----------
        orders_1 : `List[Order]`
            La prima lista di ordini
        orders_2 : `List[Order]`
            La seconda lista di ordini
        """
        for order_1, order_2 in zip(orders_1, orders_2):
            assert order_1._order_attribs_equal(order_2)


@pytest.fixture
def helpers():
    return Helpers
