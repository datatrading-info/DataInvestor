import copy
import datetime
import logging

import pandas as pd

from datainvestor import settings
from datainvestor.broker.portfolio.portfolio_event import PortfolioEvent
from datainvestor.broker.portfolio.position_handler import PositionHandler


class Portfolio(object):
    """
    Rappresenta un portafoglio di asset. Contiene un conto in contanti
    con la possibilità di sottoscrivere e prelevare fondi.
    Contiene anche un elenco di posizioni negli asset, incapsulato
    da un'istanza PositionHandler.

    Parameters
    ----------
    start_dt : datetime
       Data e ora di creazione del Portfolio.
    starting_cash : float, optional
        capitale iniziale del portafoglio. Default a 100,000 USD.
    currency: str, optional
        Valuta del portafoglio.
    portfolio_id: str, optional
        Un identificatore per il portafoglio.
    name: str, optional
        Un nome del portafoglio leggibile per gli umani.
    """

    def __init__(
        self,
        start_dt,
        starting_cash=0.0,
        currency="USD",
        portfolio_id=None,
        name=None
    ):
        """
        Inizializzare l'oggetto Portfolio con un PositionHandler,
        una cronologia degli eventi, insieme al saldo di cassa.
        Verificare che sia impostata la valuta di denominazione del portafoglio.
        """
        self.start_dt = start_dt
        self.current_dt = start_dt
        self.starting_cash = starting_cash
        self.currency = currency
        self.portfolio_id = portfolio_id
        self.name = name

        self.pos_handler = PositionHandler()
        self.history = []

        self.logger = logging.getLogger('Portfolio')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(
            '(%s) Portfolio "%s" instance initialised' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id
            )
        )

        self._initialise_portfolio_with_cash()

    def _initialise_portfolio_with_cash(self):
        """
        Inizializza il portafoglio con una valuta (predefinita) Cash
        Asset con quantità pari a 'starting_cash'.
        """
        self.cash = copy.copy(self.starting_cash)

        if self.starting_cash > 0.0:
            self.history.append(
                PortfolioEvent.create_subscription(
                    self.current_dt, self.starting_cash, self.starting_cash
                )
            )

        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id,
                round(self.starting_cash, 2),
                round(self.starting_cash, 2)
            )
        )

    @property
    def total_market_value(self):
        """
        Restituisce il valore di mercato totale del portafoglio esclusa la liquidità.
        """
        return self.pos_handler.total_market_value()

    @property
    def total_equity(self):
        """
        Restituisce il valore di mercato totale del portafoglio inclusa la liquidità.
        """
        return self.total_market_value + self.cash

    @property
    def total_unrealised_pnl(self):
        """
        Calcola la somma di tutte le posizione aperte (unrealised P&L).
        """
        return self.pos_handler.total_unrealised_pnl()

    @property
    def total_realised_pnl(self):
        """
        Calcola la somma di tutte le posizione chiuse (realised P&L).
        """
        return self.pos_handler.total_realised_pnl()

    @property
    def total_pnl(self):
        """
        Calcola la somma di tutte le posizioni (total P&L).
        """
        return self.pos_handler.total_pnl()

    def subscribe_funds(self, dt, amount):
        """
        Aggiungere fondi al portafoglio.
        """
        if dt < self.current_dt:
            raise ValueError(
                'Subscription datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'subscribe funds.' % (dt, self.current_dt)
            )
        self.current_dt = dt

        if amount < 0.0:
            raise ValueError(
                'Cannot credit negative amount: '
                '%s to the portfolio.' % amount
            )

        self.cash += amount

        self.history.append(
            PortfolioEvent.create_subscription(self.current_dt, amount, self.cash)
        )

        self.logger.info(
            '(%s) Funds subscribed to portfolio "%s" '
            '- Credit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.cash, 2)
            )
        )

    def withdraw_funds(self, dt, amount):
        """
        Prelevare fondi dal portafoglio se c'è abbastanza
        liquidità per farlo.
        """
        # Controlla che l'importo sia positivo e che ci sia
        # abbastanza nel portafoglio per prelevare i fondi
        if dt < self.current_dt:
            raise ValueError(
                'Withdrawal datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'withdraw funds.' % (dt, self.current_dt)
            )
        self.current_dt = dt

        if amount < 0:
            raise ValueError(
                'Cannot debit negative amount: '
                '%0.2f from the portfolio.' % amount
            )

        if amount > self.cash:
            raise ValueError(
                'Not enough cash in the portfolio to '
                'withdraw. %s withdrawal request exceeds '
                'current portfolio cash balance of %s.' % (
                    amount, self.cash
                )
            )

        self.cash -= amount

        self.history.append(
            PortfolioEvent.create_withdrawal(self.current_dt, amount, self.cash)
        )

        self.logger.info(
            '(%s) Funds withdrawn from portfolio "%s" '
            '- Debit: %0.2f, Balance: %0.2f' % (
                self.current_dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                self.portfolio_id, round(amount, 2),
                round(self.cash, 2)
            )
        )

    def transact_asset(self, txn):
        """
        Regola le posizioni per tenere conto di una transazione.
        """
        if txn.dt < self.current_dt:
            raise ValueError(
                'Transaction datetime (%s) is earlier than '
                'current portfolio datetime (%s). Cannot '
                'transact assets.' % (txn.dt, self.current_dt)
            )
        self.current_dt = txn.dt

        txn_share_cost = txn.price * txn.quantity
        txn_total_cost = txn_share_cost + txn.commission

        if txn_total_cost > self.cash:
            if settings.PRINT_EVENTS:
                print(
                    'WARNING: Not enough cash in the portfolio to '
                    'carry out transaction. Transaction cost of %s '
                    'exceeds remaining cash of %s. Transaction '
                    'will proceed with a negative cash balance.' % (
                        txn_total_cost, self.cash
                    )
                )

        self.pos_handler.transact_position(txn)

        self.cash -= txn_total_cost

        # Dettagli sulla cronologia del portafoglio
        direction = "LONG" if txn.direction > 0 else "SHORT"
        description = "%s %s %s %0.2f %s" % (
            direction, txn.quantity, txn.asset.upper(),
            txn.price, datetime.datetime.strftime(txn.dt, "%d/%m/%Y")
        )
        if direction == "LONG":
            pe = PortfolioEvent(
                dt=txn.dt, type='asset_transaction',
                description=description,
                debit=round(txn_total_cost, 2), credit=0.0,
                balance=round(self.cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted LONG in portfolio "%s" '
                '- Debit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    round(txn_total_cost, 2), round(self.cash, 2)
                )
            )
        else:
            pe = PortfolioEvent(
                dt=txn.dt, type='asset_transaction',
                description=description,
                debit=0.0, credit=-1.0 * round(txn_total_cost, 2),
                balance=round(self.cash, 2)
            )
            self.logger.info(
                '(%s) Asset "%s" transacted SHORT in portfolio "%s" '
                '- Credit: %0.2f, Balance: %0.2f' % (
                    txn.dt.strftime(settings.LOGGING["DATE_FORMAT"]),
                    txn.asset, self.portfolio_id,
                    -1.0 * round(txn_total_cost, 2), round(self.cash, 2)
                )
            )
        self.history.append(pe)

    def portfolio_to_dict(self):
        """
        Stampa le informazioni sulle posizioni di portafoglio in un
        dizionario con Asset come chiavi e sotto-dizionari come valori.
        Questo esclude contanti.

        Returns
        -------
        `dict`
            Le posizioni nel portafoglio.
        """
        holdings = {}
        for asset, pos in self.pos_handler.positions.items():
            holdings[asset] = {
                "quantity": pos.net_quantity,
                "market_value": pos.market_value,
                "unrealised_pnl": pos.unrealised_pnl,
                "realised_pnl": pos.realised_pnl,
                "total_pnl": pos.total_pnl
            }
        return holdings

    def update_market_value_of_asset(
        self, asset, current_price, current_dt
    ):
        """
        Aggiorna il valore di mercato dell'asset al prezzo
        e alla data attuali.
        """
        if asset not in self.pos_handler.positions:
            return
        else:
            if current_price < 0.0:
                raise ValueError(
                    'Current trade price of %s is negative for '
                    'asset %s. Cannot update position.' % (
                        current_price, asset
                    )
                )

            if current_dt < self.current_dt:
                raise ValueError(
                    'Current trade date of %s is earlier than '
                    'current date %s of asset %s. Cannot update '
                    'position.' % (
                        current_dt, self.current_dt, asset
                    )
                )

            self.pos_handler.positions[asset].update_current_price(
                current_price, current_dt
            )

    def history_to_df(self):
        """
        Crea un Pandas DataFrame della storia del portafoglio.
        """
        records = [pe.to_dict() for pe in self.history]
        return pd.DataFrame.from_records(
            records, columns=[
                "date", "type", "description", "debit", "credit", "balance"
            ]
        ).set_index(keys=["date"])
