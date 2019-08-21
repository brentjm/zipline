"""Functions to implement the commission free trading strategy.

Brent Maranzano
July 29, 2018

The idea is to create a continous series of buying and selling commission free
ETFs to minimze transaction costs. Commission free ETFs are required to be held
for 30 days (LIFO accounting) prior to selling or are assesed trading fees.
"""

import sys
from datetime import datetime, timedelta
from time import sleep
import numpy as np
import pandas as pd
from pdb import set_trace


class CFStrategy:
    """Implement the commission free trading strategy.

    class attributes:
    _td_api: instantiated class of the TDAmeritradeAPI
    etf_bars: Pandas DataFrame of the price history of the commission
    free ETFs.
    sellable_etf_positions: Pandas DataFrame of commission free ETFs that are currently
    in the portfolio and have been held for the required 30 days or more.
    possible_etf_buys: Set of commission free ETFs that are not currently
    held and have no scheduled trades.
    """
    def __init__(self, td_api=None, hdf_file=None):
        """Instantiate the TD API.

        Args:
        td_api (TDAmeritradeAPI): Intantiated TDAmeritradeAPI object.
        hdf_file (str): Full path filename to hdf file where data is stored.
        """
        self._td_api = td_api

        if hdf_file is not None:
            store = pd.HDFStore(hdf_file, mode="r")
            self.etf_bars = store.get("etf_bars")
            store.close()
        else:
            self._get_etf_bars()
            store = pd.HDFStore("strategy.hdf", mode="w")
            self.etf_bars.to_hdf(store, "etf_bars")
            store.close()

        self._get_sellable_etf_positions()

        self._get_possible_etf_buys()

    def _get_etf_bars(self):
        """Get the price history of the commission free ETFs.
        """
        symbols = set()
        for watchlist_name in ["CommissionFree2018-07-30"+num
                               for num in ["1", "2"]]:
            results = self._td_api.get_watchlist(name=watchlist_name)
            symbols = symbols.union([itm["instrument"]["symbol"]
                                     for itm in results["watchlistItems"]])

        end_date = datetime.today()
        start_date = end_date - timedelta(300)
        self.etf_bars = self._td_api.get_price_history(
                symbols=symbols, start_date=start_date, end_date=end_date)

    def _get_sellable_etf_positions(self):
        """Get positions that are commission free ETFs that have been held for
        the required 30 days.
        """
        positions = self._td_api.get_positions()
        positions.index = positions["symbol"]

        trades = self._td_api.get_trades(to_date=datetime.today(),
                     from_date=datetime.today() - timedelta(35))
        trades = trades.loc[trades["instruction"] == "BUY"]

        etfs = set(self.etf_bars.columns.get_level_values(0))

        self.etf_positions = positions.loc[set(positions["symbol"].values)
                         .intersection(etfs) - set(trades["symbol"].values)]

    def _get_possible_etf_buys(self):
        """Get the set of commission free ETFs that are not in the portfolio and
        are not in any current open orders.
        """
        etfs = set(self.etf_bars.columns.get_level_values(0))

        positions = self._td_api.get_positions()
        if len(positions) > 0:
            positions = set(positions["symbol"])
        else:
            positions = set()

        orders = self._td_api.get_simple_open_orders()
        if len(orders) > 0:
            orders = set(orders["symbol"])
        else:
            orders = set()

        self.possible_etf_buys = etfs - orders - positions

    def _estimate_30_day_return(self):
        """Provide an estimation of the 30 day return of the
        possible_etf_buys. It is expected that this functin
        will continuously be tweaked to improve performance.

        returns Numpy array ticker symbols
        """
        P = self.etf_bars.xs("close_price", axis=1, level=1)[list(self.possible_etf_buys)]
        dP = P.pct_change()[1:]

        avg_60 = dP.rolling(window=60, axis=0).sum().mean()
        last_30 = dP.iloc[-30:].sum(axis=0)

        return avg_60 - last_30

    def create_sell_orders(self, symbol, number_shares):
        """Create sell orders. The sell prices are from 0 to 2 standard
        deviations of the high-open daily price change over the previous month.
        The quantity of each order progressively increases by approximately
        a factor of 2 as the limit price increases.

        Args:
        symbol (string): Ticker symbol
        number_shares (int): Toral number of shares to sell
                             (through multiple orders).
        """
        MAX_NUMBER_ORDERS = int(min(20, number_shares))

        # Calculate quantity for each order.
        quantities = [2*x for x in range(1, MAX_NUMBER_ORDERS)]
        scale = float(number_shares) / float(sum(quantities))
        quantities = [int(scale*q) for q in quantities if int(scale*q) != 0]

        # Calculate the price for each order based on intra-day statistis
        # current_price = self._td_api.get_quotes(symbol)["regularMarketLastPrice"].values[0]
        current_price = self._td_api.get_quotes(symbol)["askPrice"].values[0]
        open_to_high = self.etf_bars.loc[slice(None), (symbol, "high")]\
            - self.etf_bars.loc[slice(None), (symbol, "open_price")].values
        avg = open_to_high.mean(axis=0)
        std = open_to_high.std(axis=0)
        lower_price = current_price + 0.1 * avg
        upper_price = current_price + (avg + 2*std)
        prices = np.linspace(lower_price, upper_price, len(quantities))

        for price, quantity in zip(prices, quantities):
            self._td_api.create_saved_order(symbol=symbol, price=price,
                quantity=quantity, instruction="SELL")

    def create_buy_orders(self, symbol, number_shares):
        """Create buy orders. The buy prices are from the current price to 0 to
        2 standard deviations below the high-open daily price change over the
        previous month.  The quantity of each order progressively increases by
        approximately a factor of 2 as the limit price decrease.

        Args:
        symbol (string): Ticker symbol
        number_shares (int): Toral number of shares to sell
                             (through multiple orders).
        """
        MAX_NUMBER_ORDERS = int(min(20, number_shares))

        # Calculate quantity for each order.
        quantities = [2*x for x in range(1, MAX_NUMBER_ORDERS)]
        scale = float(number_shares) / float(sum(quantities))
        quantities = [int(scale*q) for q in quantities if int(scale*q) != 0]

        # Calculate the price for each order based on intra-day statistis
        # current_price = self._td_api.get_quotes(symbol)["regularMarketLastPrice"].values[0]
        current_price = self._td_api.get_quotes(symbol)["askPrice"].values[0]
        open_to_high = self.etf_bars.loc[slice(None), (symbol, "high")]\
            - self.etf_bars.loc[slice(None), (symbol, "open_price")].values
        avg = open_to_high.mean(axis=0)
        std = open_to_high.std(axis=0)
        upper_price = current_price - 0.1 * avg
        lower_price = current_price - (avg + 2*std)
        prices = np.linspace(upper_price, lower_price, len(quantities))

        for price, quantity in zip(prices, quantities):
            self._td_api.create_saved_order(symbol=symbol, price=price,
                quantity=quantity, instruction="BUY")

    def run_sell_strategy(self):
        """Use the sell criteria to get a list of the within portfolio
        ETFs that should be sold, and then create saved sell orders.
        """
        sells = self.etf_positions
        sells = sells[sells["currentDayProfitLossPercentage"] > .01]

        for row in sells.iterrows():
            # row is of form (ticker, dictionary_of_asset_information),
            # so row[1] is a dictionary of assets information.
            asset = row[1]
            self.create_sell_orders(asset.name, asset["longQuantity"])
            # Pause execution to avoid TDAmeritrade from report HTTP 429 Error -
            # too many requests.
            sleep(1)

    def run_buy_strategy(self):
        """Use the buy criteria to get a list of commission free
        ETFs that should be bought, and then create saved buy orders.
        """
        buy_ranking = self._estimate_30_day_return().sort_values(ascending=False)
        tickers = buy_ranking[[0, 10]].index
        quotes = self._td_api.get_quotes(tickers)["regularMarketLastPrice"]
        number_shares = [int(500./q) for q in quotes]
        orders = zip(tickers, number_shares)

        for row in orders:
            self.create_buy_orders(row[0], row[1])
            # Pause execution to avoid TDAmeritrade from report HTTP 429 Error -
            # too many requests.
            sleep(1)


if __name__ == "__main__":
    from tdameritrade_api import TDAmeritradeAPI
    if len(sys.argv) == 3:
        td_api = TDAmeritradeAPI.create_api_from_account_file(sys.argv[1])
        strategy = CFStrategy(td_api=td_api, hdf_file=sys.argv[2])
    else:
        print("""Usage:
        python cf_strategy path_to_account_info_file path_to_historic_data_hdf_file""")
        raise OSError
    strategy.run_buy_strategy()
    strategy.run_sell_strategy()
