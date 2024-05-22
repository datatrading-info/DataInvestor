from abc import ABCMeta, abstractmethod


class Broker(object):
    """
    Questa classe astratta fornisce un'interfaccia per un'entità broker
    generica. Sia i broker simulati che quelli live saranno derivati da
    questo ABC. Garantisce che la logica specifica dell'algoritmo di
    trading sia completamente identica sia per gli ambienti simulati
    che per quelli live.

    Il Broker ha una valuta associata denominata master attraverso la
    quale avverranno tutti i depositi e i prelievi.

    L'entità Broker può supportare più sottoportfolio, ciascuno con la propria
    gestione separata di PnL. I singoli PnL di ciascun sottoportafoglio
    possono essere aggregati per generare un PnL a livello di account.

    Il Broker può eseguire ordini. Contiene una coda di ordini aperti,
    necessari per gestire situazioni di mercato chiuso.

    Il Broker supporta anche gli eventi cronologici individuali per ogni
    sottoportafoglio, che possono essere aggregati, insieme alla cronologia
    del conto, per produrre una cronologia di trading completa per il conto.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe_funds_to_account(self, amount):
        raise NotImplementedError(
            "Should implement subscribe_funds_to_account()"
        )

    @abstractmethod
    def withdraw_funds_from_account(self, amount):
        raise NotImplementedError(
            "Should implement withdraw_funds_from_account()"
        )

    @abstractmethod
    def get_account_cash_balance(self, currency=None):
        raise NotImplementedError(
            "Should implement get_account_cash_balance()"
        )

    @abstractmethod
    def get_account_total_equity(self):
        raise NotImplementedError(
            "Should implement get_account_total_equity()"
        )

    @abstractmethod
    def create_portfolio(self, portfolio_id, name):
        raise NotImplementedError(
            "Should implement create_portfolio()"
        )

    @abstractmethod
    def list_all_portfolios(self):
        raise NotImplementedError(
            "Should implement list_all_portfolios()"
        )

    @abstractmethod
    def subscribe_funds_to_portfolio(self, portfolio_id, amount):
        raise NotImplementedError(
            "Should implement subscribe_funds_to_portfolio()"
        )

    @abstractmethod
    def withdraw_funds_from_portfolio(self, portfolio_id, amount):
        raise NotImplementedError(
            "Should implement withdraw_funds_from_portfolio()"
        )

    @abstractmethod
    def get_portfolio_cash_balance(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_cash_balance()"
        )

    @abstractmethod
    def get_portfolio_total_equity(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_total_equity()"
        )

    @abstractmethod
    def get_portfolio_as_dict(self, portfolio_id):
        raise NotImplementedError(
            "Should implement get_portfolio_as_dict()"
        )

    @abstractmethod
    def submit_order(self, portfolio_id, order):
        raise NotImplementedError(
            "Should implement submit_order()"
        )
