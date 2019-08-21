"""
Module to contain functions for analyzing price bars.

Brent Maranzano
August 28, 2018
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


def calc_differentials(bars):
    """
    Calculate the price differentials:
        cc_{i} = (close_price_{i} - close_price_{i-1}) / close_price_{i-1}
        co_{i} = (open_price_{i} - close_price_{i-1}) / close_price_{i-1}
        oc_{i} = (close_price_{i} - open_price_{i}) / open_price_{i}
        high_{i} = (high_{i} - open_price_{i}) / open_price_{i}
        low_{i} = (low_{i} - open_price_{i}) / open_price_{i}

    bars: Pandas mult-index [dates, (symbol, price_type)]
       where price_type is [open_price, high, low, close_price]

    returns Pandas mult-index with structure of bars above
    """
    open_price = bars.loc[:, (slice(None), "open_price")].iloc[1:].values
    close_price = bars.loc[:, (slice(None), "close_price")].iloc[1:].values
    high = bars.loc[:, (slice(None), "high")].iloc[1:].values
    low = bars.loc[:, (slice(None), "low")].iloc[1:].values
    previous_close_price =\
        bars.loc[:, (slice(None), "close_price")].iloc[:-1].values

    cc = (close_price - previous_close_price) / previous_close_price
    co = (open_price - previous_close_price) / previous_close_price
    oc = (close_price - open_price) / open_price
    high = (high - open_price) / open_price
    low = (low - open_price) / open_price

    symbols = bars.columns.get_level_values(0).unique()
    data = pd.DataFrame(index=bars.index[1:],
                        columns=pd.MultiIndex.from_product(
                         [symbols, ["cc", "co", "oc", "high", "low"]]))

    data.loc[:, (slice(None), "cc")] = cc
    data.loc[:, (slice(None), "co")] = co
    data.loc[:, (slice(None), "oc")] = oc
    data.loc[:, (slice(None), "high")] = high
    data.loc[:, (slice(None), "low")] = low

    return data


def scaled_price_change(prices):
    """Calculate the scaled total price change over a range of
    window sizes.
    (S dP - avg(S dP)) / <var(S dP)> where S is sum over some range t

    Arguments:
    prices (pandas DataFrame): Price as a function of time, oldest
    data at position zero, and most current data at end of series.

    returns (pandas DataFrame)
    scaled price change (index position corresponds to time frame.
    """
    dP = prices.pct_change().iloc[1:][::-1]

    max_window_length = int(len(prices) / 4)
    scaled_dP = pd.DataFrame(index=range(1, max_window_length),
                             columns=prices.columns)

    for i in range(1, max_window_length):
        avg = dP.rolling(window=i, axis=0).sum().mean()
        std = dP.rolling(window=i, axis=0).sum().std()
        scaled_dP.loc[i] = (dP.iloc[:i].mean() - avg)
        scaled_dP.loc[i] = (dP.iloc[:i].mean())

    return scaled_dP


def pca_analysis(prices):
    """Calculate the principal component analysis of the prices changes.

    Arguments:
    prices (pandas DataFrame): Price as a function of time, oldest
    data at position zero, and most current data at end of series.

    returns (dict) {norm_loadings: DataFrame, proj: DataFrame}
    """
    X = prices.apply(lambda x: (x - x.mean()) / x.std())
    n_components = 4
    pca = PCA(n_components=n_components).fit(X)
    loadings = pd.DataFrame(index=prices.index,
                            columns=range(1, n_components+1),
                            data=pca.transform(X))
    norm_loadings = loadings.apply(lambda x: x/np.sqrt(np.dot(x, x)))
    proj = pd.DataFrame(index=range(1, n_components+1),
                        columns=prices.columns,
                        data=np.dot(norm_loadings.T.values, prices.values))
    return dict(norm_loadings=norm_loadings, projections=proj)
