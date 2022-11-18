import uuid

import numpy as np


class Order(object):
    """
    Rappresenta l'invio di un ordine da un'entità di algoritmo
    di trading a un intermediario per l'esecuzione.

    Una commissione può essere aggiunta per sovrascrivere il
    modello di commissione, se noto. E' possibile aggiungere
    un order_id, altrimenti verrà assegnato in modo casuale.

    Parameters
    ----------
    dt : `pd.Timestamp`
        La data e l'ora in cui è stato creato l'ordine.
    asset : `Asset`
        L'asset da negoziare con l'ordine.
    quantity : `int`
        La quantità dell'asset da negoziare.
        Una quantità negativa significa uno short.
    commission : `float`, optional
        Se la commissione è nota, può essere aggiunta.
    order_id : `str`, optional
        L'ID dell'ordine, se noto.
    """

    def __init__(
        self,
        dt,
        asset,
        quantity,
        commission=0.0,
        order_id=None
    ):
        self.created_dt = dt
        self.cur_dt = dt
        self.asset = asset
        self.quantity = quantity
        self.commission = commission
        self.direction = np.copysign(1, self.quantity)
        self.order_id = self._set_or_generate_order_id(order_id)

    def _order_attribs_equal(self, other):
        """
        Asserts whether all attributes of the Order are equal
        with the exception of the order ID.

        Used primarily for testing that orders are generated correctly.

        Verifica se tutti gli attributi dell'ordine sono uguali
        ad eccezione dell'ID ordine.

        Utilizzato principalmente per verificare che gli ordini
        vengano generati correttamente.

        Parameters
        ----------
        other : `Order`
            L'ordine con cui confrontare l'uguaglianza degli attributi.

        Returns
        -------
        `Boolean`
            Se gli attributi dell'ID non ordine sono uguali.
        """
        if self.created_dt != other.created_dt:
            return False
        if self.cur_dt != other.cur_dt:
            return False
        if self.asset != other.asset:
            return False
        if self.quantity != other.quantity:
            return False
        if self.commission != other.commission:
            return False
        if self.direction != other.direction:
            return False
        return True

    def __repr__(self):
        """
            Genera una rappresentazione di stringa dell'oggetto

        Returns
        -------
        `str`
            Rappresentazione di stringa dell'istanza dell'ordine.
        """
        return (
            "Order(dt='%s', asset='%s', quantity=%s, "
            "commission=%s, direction=%s, order_id=%s)" % (
                self.created_dt, self.asset, self.quantity,
                self.commission, self.direction, self.order_id
            )
        )

    def _set_or_generate_order_id(self, order_id=None):
        """
        Imposta o genera un ID ordine univoco per l'ordine, utilizzando un UUID.

        Parameters
        ----------
        order_id : `str`, optional
            Una sostituzione dell'ID ordine facoltativa.

        Returns
        -------
        `str`
            La stringa dell'ID dell'ordine per l'ordine.
        """
        if order_id is None:
            return uuid.uuid4().hex
        else:
            return order_id
