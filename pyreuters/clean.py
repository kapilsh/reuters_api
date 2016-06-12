import pandas as pd
import numpy as np
from statsmodels.robust.scale import mad


def __check_quotes__(qdata):
    col_names = qdata.columns
    if not np.any(col_names == 'Bid'):
        raise ValueError('Could not find Bid in column names')
    if not np.any(col_names == 'Ask'):
        raise ValueError('Could not find Ask in column names')
    if not np.any(col_names == 'BidSize'):
        raise ValueError('Could not find BidSize in column names')
    if not np.any(col_names == 'AskSize'):
        raise ValueError('Could not find AskSize in column names')


def __check_trades__(tdata):
    col_names = tdata.columns
    if not np.any(col_names == 'Price'):
        raise ValueError('Could not find Price in column names')
    if not np.any(col_names == 'Volume'):
        raise ValueError('Could not find Volume in column names')


def check_trades(trades):
    __check_trades__(trades)
    return trades


def check_quotes(quotes):
    __check_quotes__(quotes)
    return quotes


def clean_quotes(quotes,
                 how=("zero_quotes", "error_quotes",
                      "outliers", "large_spreads")):
    [x(quotes) for x in how]
    return quotes


def clean_trades(trades, how="zero_prices"):
    [x(trades) for x in list(how)]
    return trades


def no_zero_quotes(quotes):
    __check_quotes__(quotes)
    original_count = len(quotes.index)
    quotes = quotes.ix[quotes.apply(__non_zero_quote, axis=1)]
    final_count = len(quotes.index)
    print("Removed {} zero quotes".format(original_count - final_count))
    return quotes


def __non_zero_quote(row):
    return (row.Bid != 0 and row.Ask != 0 and row.BidSize != 0 and
            row.AskSize != 0) or (row.Bid != 0 and row.BidSize != 0) \
           or (row.Ask != 0 and row.AskSize != 0)


def no_zero_prices(trades):
    original_count = len(trades.index)
    trades = trades.ix[trades.apply(__non_zero_price, axis=1)]
    final_count = len(trades.index)
    print("Removed {} zero priced trades".format(original_count - final_count))
    return trades


def __non_zero_price(row):
    return not(row.Price == 0 or row.Volume == 0 or
               np.isnan(row.Price) or np.isnan(row.Volume))


def rm_large_spreads(quotes, func=np.median, mult=50, verbose=False):
    __check_quotes__(quotes)
    temp = quotes.ffill()
    original_count = len(quotes.index)
    spreads = temp.Ask - temp.Bid
    indicator = func(spreads)
    to_keep = spreads <= mult*indicator
    quotes = quotes.ix[to_keep]
    final_count = len(quotes.index)
    print("Removed {} large spread quotes".format(original_count - final_count))
    return quotes


def rm_quote_outliers(quotes, mult=10, window=50, center=np.median,
                      filter_type='advanced'):
    __check_quotes__(quotes)
    original_count = len(quotes.index)
    cleaned_qd = quotes
    if original_count > window:
        window = np.floor(window/2) * 2
        temp = quotes.ffill().bfill()
        mid_quotes = (temp.Bid + temp.Ask)/2
        mq_mad = mad(mid_quotes, center=center)
        if mq_mad == 0:
            m = mid_quotes
            s = np.append([True],
                          (m[1:len(m)].values - m[0:(len(m)-1)].values) != 0)
            mq_mad = mad(mid_quotes[s])

        def __modified_median__(arr):
            w = len(arr)
            return np.median(np.append(arr[0:(w-1)/2], arr[(w/2 + 1):w]))

        roll_meds = None
        meds = pd.rolling_apply(mid_quotes, window=window + 1,
                                func=__modified_median__, center=True)

        if filter_type == 'standard':
            roll_meds = meds.ffill().bfill()

        if filter_type == 'advanced':
            def __forward_median__(arr):
                w = (len(arr) - 1)/2
                return np.median(arr[w+1:])

            def __backward_median__(arr):
                w = (len(arr) - 1)/2
                return np.median(arr[:w])

            def __closest_to_mid_quote__(qq):
                qq[np.isnan(qq)] = qq[3]
                diff = np.abs(qq[0:2] - qq[3])
                select = np.min(diff) == diff
                value = qq[select]
                if len(value) > 1:
                    value = np.median(value)
                return value

            all_matrix = np.zeros((len(mid_quotes), 4))
            all_matrix[:, 0] = meds
            all_matrix[:, 1] = pd.rolling_apply(mid_quotes,
                                                window=2*window + 1,
                                                func=__forward_median__,
                                                center=True)
            all_matrix[:, 2] = pd.rolling_apply(mid_quotes,
                                                window=2*window + 1,
                                                func=__backward_median__,
                                                center=True)
            all_matrix[:, 3] = mid_quotes
            roll_meds = np.apply_along_axis(__closest_to_mid_quote__,
                                            axis=1, arr=all_matrix)

        max_criterion = roll_meds + mult * mq_mad
        min_criterion = roll_meds - mult * mq_mad
        min_condition = np.less(min_criterion, mid_quotes.values)
        max_condition = np.less(mid_quotes.values, max_criterion)
        condition = np.logical_and(min_condition, max_condition)
        cleaned_qd = quotes.ix[condition]
        final_count = len(cleaned_qd.index)
    print("Removed {} outliers".format(original_count - final_count))
    return cleaned_qd


def rm_erroneous_quotes(quotes):
    __check_quotes__(quotes)
    original_count = len(quotes.index)
    temp = quotes.ffill()
    quotes = quotes.ix[temp.Bid < temp.Ask]
    final_count = len(quotes.index)
    print("Removed {} erroneous quotes".format(original_count - final_count))
    return quotes

clean_quote_funcs = {
    "zero_quotes": no_zero_prices,
    "error_quotes": rm_erroneous_quotes,
    "outliers": rm_quote_outliers,
    "large_spreads": rm_large_spreads
}


clean_trade_funcs = {
    "zero_prices": no_zero_prices
}
