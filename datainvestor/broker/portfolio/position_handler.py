from collections import OrderedDict

from datainvestor.broker.portfolio.position import Position


class PositionHandler(object):
    """
    Una classe che tiene traccia e aggiorna l'elenco corrente delle
     istanze di posizione archiviate in un'entità Portfolio.
    """

    def __init__(self):
        """
        Inizializzare l'oggetto PositionHandler per generare un
        dizionario ordinato contenente le posizioni correnti.
        """
        self.positions = OrderedDict()

    def transact_position(self, transaction):
        """
        Execute the transaction and update the appropriate
        position for the transaction's asset accordingly.
        Eseguire la transazione e aggiornare di conseguenza la
        posizione appropriata dell'asset della transazione.
        """
        asset = transaction.asset
        if asset in self.positions:
            self.positions[asset].transact(transaction)
        else:
            position = Position.open_from_transaction(transaction)
            self.positions[asset] = position

        # Rimuove la posizione se ha quantità zero
        if self.positions[asset].net_quantity == 0:
            del self.positions[asset]

    def total_market_value(self):
        """
        Calcola la somma di tutti i valori di mercato delle posizioni.
        """
        return sum(
            pos.market_value
            for asset, pos in self.positions.items()
        )

    def total_unrealised_pnl(self):
        """
        Calcola la somma dei profitti e delle perdite non realizzati di tutte le posizioni.
        """
        return sum(
            pos.unrealised_pnl
            for asset, pos in self.positions.items()
        )

    def total_realised_pnl(self):
        """
        Calcola la somma dei profitti e delle perdite realizzati di tutte le posizioni.
        """
        return sum(
            pos.realised_pnl
            for asset, pos in self.positions.items()
        )

    def total_pnl(self):
        """
        Calcola la somma dei profitti e delle perdite di tutte le posizioni.
        """
        return sum(
            pos.total_pnl
            for asset, pos in self.positions.items()
        )
