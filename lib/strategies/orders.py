"""Smart/auto-calculated orders."""
# from datetime import datetime, timedelta
import math


def easy_bracket(symbol=None, instruction=None, quantity=None,
                 amount=1000, limit_percent=None, profit_percent=None,
                 quotes=None):
    """Calculate bracket order for symbol using a limit provided by
    limit_percent.

    Arguments
    symbol (str): Ticker symbol
    instruction (str): "BUY" | "SELL"
    quantity (int): Number of shares
    amount (float): Amount in dollars to trade
    limit_percent (float): Percent change from current quote to set limit.
    profit_percent (float): Percent change from limit price to take profit.
    quotes (pandas Series): Current asset price

    Returns (dict) Parameters necessary to place a bracket order.
    """
    # Calculate a reasonable change if limit_percent is not given.
    if limit_percent is None:
        if instruction == "BUY":
            limit_percent = -0.3
        if instruction == "SELL":
            limit_percent = 0.3

    # Calculate a reasonable change if limit_percent is not given.
    if profit_percent is None:
        if instruction == "BUY":
            profit_percent = 0.3
        if instruction == "SELL":
            profit_percent = -0.3

    # Calculate the limit price from the limit_percent.
    limit_price = round(quotes[symbol] * (1 + limit_percent/100.), 2)
    # Calculate the profit price from the limit_price.
    profit_price = round(limit_price * (1 + profit_percent/100.), 2)

    # Calculate quantity if amount was provided.
    if quantity is None:
        quantity = int(amount / quotes[symbol])

    return {
        'symbol': symbol,
        'instruction': instruction,
        'quantity': quantity,
        'price': limit_price,
        'tif': "DAY",
        'outside_rth': True,
        'profit_price': profit_price,
        'stop_price': None
    }


def smart_bracket(symbol=None, instruction=None, quantity=100,
                  amount=1000, limit_prob=0.5, profit_prob=0.5,
                  bars=None, quotes=None):
    """Calculate bracket order for symbol. The larger the value of the
    argument probability, the more probable the trade will fill.

    Arguments
    symbol (str): Ticker symbol
    instruction (str): "BUY" | "SELL"
    quantity (int): Number of shares
    amount (float): Number of dollars
    limit_prob (float): Probability of executing the limit order.
    profit_prob (float): Probability of executing the profit order
    bars (pandas DataFrame): Ticker bar data.
    quotes (pandas Series): Current asset price

    Returns (dict) Parameters necessary to place a bracket order.
    """
    # Number of days in price history to use for estimating statistics
    n_days = 50

    prices = bars[symbol].iloc[-n_days:]
    low = prices['open_price'] - prices['low']
    high = prices['high'] - prices['open_price']
    hilo = prices['high'] - prices['low']

    quote = quotes[symbol]
    if instruction == "BUY":
        limit_price = quote - low.quantile(1 - limit_prob)
        profit_price = limit_price + hilo.quantile(1 - profit_prob)
    elif instruction == "SELL":
        limit_price = quote + high.quantile(1 - limit_prob)
        profit_price = limit_price - hilo.quantile(1 - profit_prob)

    # Calculate the quantity if only the amount was provided.
    quantity = int(amount / quote)

    return {
        'symbol': symbol,
        'instruction': instruction,
        'quantity': quantity,
        'price': round(limit_price, 2),
        'tif': "DAY",
        'outside_rth': True,
        'profit_price': round(profit_price, 2),
        'stop_price': None
    }


def auto_pegged(symbol=None, instruction=None, amount=1000, ref_symbol=None,
                quotes=None):
    """Calculate the parameters for a reasonable pegged order.

    Arguments:
    symbol (str): Ticker symbol.
    instruction (str): "BUY" | "SELL"
    amount (float): Number of dollars
    ref_symbol (str): Ticker symbol for reference asset

    Returns (dict): Parameters necessary to place a pegged order.
    """
    quote = quotes[symbol]
    ref_quote = quotes[ref_symbol]

    quantity = int(amount / quote)

    # The lower valued asset price change will be 0.01. The higher
    # priced asset will change by one cent time the ratio of the prices.
    ratio = quote / ref_quote
    if ratio > 1:
        ref_change_amount = 0.01
        peg_change_amount = 0.01 * math.floor(ratio)
    if ratio <= 1:
        peg_change_amount = 0.01
        ref_change_amount = 0.01 * math.ceil(1. / ratio)

    ref_price = ref_quote
    if instruction == "BUY":
        starting_price = round(quote * 0.995, 2)
    elif instruction == "SELL":
        starting_price = round(quote * 1.005, 2)

    ref_lower_price = round(0.9 * ref_quote, 2)
    ref_upper_price = round(1.1 * ref_quote, 2)

    return {
        'symbol': symbol,
        'instruction': instruction,
        'quantity': quantity,
        'starting_price': starting_price,
        'outside_rth': False,
        'tif': "DAY",
        'peg_change_amount': peg_change_amount,
        'ref_change_amount': ref_change_amount,
        'ref_symbol': ref_symbol,
        'ref_price': ref_price,
        'ref_lower_price': ref_lower_price,
        'ref_upper_price': ref_upper_price
    }
