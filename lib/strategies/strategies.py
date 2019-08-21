"""Trading strategies"""
import orders


def easy_volatility(symbol=None, bars=None, quotes=None):
    """Create as series of BUY and SELL bracket orders intended to profit off of
    daily volatility.

    Arguments:
    symbol (str): Ticker symbol.
    bars (pandas DataFrame): Ticker bar data.
    quotes (pandas Series): Current asset price

    Returns (list): List of dictionaries, each element defines a bracket order.
    """

    params = [
        {'instruction': "BUY", 'amount': 1000, 'percent': -.2},
        {'instruction': "BUY", 'amount': 2000, 'percent': -.5},
        {'instruction': "SELL", 'amount': 1000, 'percent': .2},
        {'instruction': "SELL", 'amount': 2000, 'percent': .5},
    ]

    bracket_orders = list()
    for p in params:
        bracket_orders.append(
            orders.easy_bracket(symbol=symbol, instruction=p['instruction'],
                                amount=p['amount'],
                                percent=p['percent'],
                                bars=bars, quotes=quotes)
        )
    return bracket_orders


def long_brackets(symbol=None, bars=None, quotes=None):
    """Create as series of BUY bracket orders intended to profit off of rising prices.

    Arguments:
    symbol (str): Ticker symbol.
    bars (pandas DataFrame): Ticker bar data.
    quotes (pandas Series): Current asset price

    Returns (list): List of dictionaries, each element defines a bracket order.
    """

    params = [
        {'instruction': "BUY", 'amount': 1000, 'percent': -.1},
        {'instruction': "BUY", 'amount': 1500, 'percent': -.3},
        {'instruction': "BUY", 'amount': 2000, 'percent': -.5},
    ]

    bracket_orders = list()
    for p in params:
        bracket_orders.append(
            orders.easy_bracket(symbol=symbol, instruction=p['instruction'],
                                amount=p['amount'],
                                percent=p['percent'],
                                bars=bars, quotes=quotes)
        )
    return bracket_orders


def short_brackets(symbol=None, bars=None, quotes=None):
    """Create as series of SELL bracket orders intended to profit off of falling prices.

    Arguments:
    symbol (str): Ticker symbol.
    bars (pandas DataFrame): Ticker bar data.
    quotes (pandas Series): Current asset price

    Returns (list): List of dictionaries, each element defines a bracket order.
    """

    params = [
        {'instruction': "SELL", 'amount': 1000, 'percent': .1},
        {'instruction': "SELL", 'amount': 1500, 'percent': .3},
        {'instruction': "SELL", 'amount': 2000, 'percent': .5},
    ]

    bracket_orders = list()
    for p in params:
        bracket_orders.append(
            orders.easy_bracket(symbol=symbol, instruction=p['instruction'],
                                amount=p['amount'],
                                percent=p['percent'],
                                bars=bars, quotes=quotes)
        )
    return bracket_orders


def smart_volatility(symbol=None, bias=0, bars=None, quotes=None):
    """Create as series of BUY and SELL bracket orders intended to profit off of
    daily volatility.

    Arguments:
    symbol (str): Ticker symbol.
    bias (float): Offset of bracket probability positive for emphasis on
        buying, negative for emphasis on selling.
    bars (pandas DataFrame): Ticker bar data.
    quotes (pandas Series): Current asset price

    Returns (list): List of dictionaries, each element defines a bracket order.
    """

    params = [
        {'instruction': "BUY", 'amount': 1000, 'probability': 0.7 + bias},
        {'instruction': "BUY", 'amount': 2000, 'probability': 0.3 + bias},
        {'instruction': "SELL", 'amount': 1000, 'probability': 0.7 - bias},
        {'instruction': "SELL", 'amount': 2000, 'probability': 0.3 - bias},
    ]

    bracket_orders = list()
    for p in params:
        bracket_orders.append(
            orders.smart_bracket(symbol=symbol, instruction=p['instruction'],
                                 amount=p['amount'],
                                 probability=p['probability'],
                                 bars=bars, quotes=quotes)
        )
    return bracket_orders
