import pandas as pd
import logging
import dateutil
import backtrader as bt


def train_test_split(data, ts_size=0.7):
    """ """
    size = len(data)
    train_size = int(size * ts_size)
    xtrain = data.iloc[0:train_size]

    x_val = data.iloc[train_size:size]
    size_val = len(x_val)
    size_xtest = int(0.3 * size_val)
    xtest = x_val.iloc[0:size_xtest]
    xval = x_val.iloc[size_xtest:size_val]

    return xtest, xval, xtrain


def to_date(x):
    """ """

    x = pd.Timestamp(x, unit="s").date().__str__()
    return x


def extract_period(data, _min=None, _max=None):
    """ """

    result = {}

    if _min is None and _max is None:
        _min = dateutil.parser.parse(data["date"].min()).date()
        _max = dateutil.parser.parse(data["date"].max()).date()

    else:
        _min = dateutil.parser.parse(_min).date()

        _max = dateutil.parser.parse(_max).date()

    result["fromdate"] = _min
    result["todate"] = _max

    return result


# ===========================
def _formatpandas(data, fromdate=None, todate=None):

    period = extract_period(data, fromdate, todate)
    # print(period)

    # data = btfeed.GenericCSVData(
    # 			dataname=path,
    # 			fromdate=period['fromdate'],
    # 			todate=period['todate'],
    # 			nullvalue=0.0,
    # 			dtformat=('%Y-%m-%d'))

    _min = period["fromdate"]
    _max = period["todate"]
    data["date"] = data["date"].apply(lambda x: dateutil.parser.parse(x).date())

    data = data[data["date"] >= _min]
    data = data[data["date"] <= _max]

    # =================================
    data["date"] = data["date"].apply(lambda x: pd.Timestamp(x))
    # data["date"] = data["date"].apply(lambda x: datetime.datetime(x))

    data = data.set_index("date")
    data.index.name = "datetime"

    data = bt.feeds.PandasData(dataname=data)

    return data
