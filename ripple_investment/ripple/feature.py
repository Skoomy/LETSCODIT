import pandas as pd
import numpy as np

# ========
def _todate(data):
    """ """

    data["time"] = data["time"].apply(lambda e: pd.Timestamp(e, unit="s").date())
    return data


class Trend:
    def __init__(self, trend):
        self.trend = trend

    # ===========================================
    def _trend_decreasing(self, datum, length=5):
        """ """
        data = datum.copy()
        if "close" not in data.columns:
            return data

        def stricly_decreasing(series, n):
            a = all([i > j for i, j in zip(series[-n:], series[1:])])
            return a

        close = data["close"]

        decreasing = close.rolling(length, min_periods=length).apply(
            stricly_decreasing, args=(length,), raw=False
        )
        #     Percentage change between the current and a prior element.
        decreasing_perc = close.pct_change(periods=length)
        decreasing.fillna(0, inplace=True)
        decreasing = decreasing.astype(bool)
        data["trend_decreasing_last_{}_days".format(length)] = decreasing
        data["trend_decreasing_last_{}_days".format(length)] = data[
            "trend_decreasing_last_{}_days".format(length)
        ].shift(1)
        data["trend_decreasing_perc_{}".format(length)] = decreasing_perc
        #     data['decreasing_shift_last_2_days'] = data['trend_decreasing_last_2_days'].shift(1)

        return data

    # ===========================================
    def _trend_increasing(self, datum, length=3):
        """ """
        data = datum.copy()
        if "close" not in data.columns:
            return data

        def stricly_decreasing(series, n):
            a = all([i < j for i, j in zip(series[-n:], series[1:])])
            return a

        close = data["close"]

        decreasing = close.rolling(length, min_periods=length).apply(
            stricly_decreasing, args=(length,), raw=False
        )
        #     Percentage change between the current and a prior element.
        decreasing_perc = close.pct_change(periods=length)
        decreasing.fillna(0, inplace=True)
        decreasing = decreasing.astype(bool)
        data["trend_increasing_last_{}_days".format(length)] = decreasing
        data["trend_increasing_last_{}_days".format(length)] = data[
            "trend_increasing_last_{}_days".format(length)
        ].shift(1)
        data["trend_increasing_perc_{}".format(length)] = decreasing_perc
        #     data['decreasing_shift_last_2_days'] = data['trend_decreasing_last_2_days'].shift(1)

        return data

    def fit(self, data, lenght):
        self.datum = data
        if self.trend == "decreasing":
            return self._trend_decreasing(self.datum, lenght)

        if self.trend == "increasing":
            return self._trend_increasing(self.datum, lenght)


def _trend(data, trend):
    """ """
    result = []
    if trend not in ["increasing", "decreasing"]:
        raise

    for k in range(2, 10):

        data = Trend(trend).fit(data, k)

        col = f"trend_{trend}_last_{k}_days"

        res = data[col].value_counts().to_dict()
        tmp = data[data[f"trend_{trend}_last_{k}_days"] == True]
        elem = {}
        elem["name"] = col
        try:
            elem[f"trend_{trend}_perc"] = np.mean(tmp[f"trend_{trend}_perc_{k}"].values)
        except Exception as error:
            raise error
        try:
            elem["true"] = res[True]
        except:
            pass
        try:
            elem["false"] = res[False]
        except:
            pass
        result.append(elem)

    result = pd.DataFrame(result)
    return data, result


COLS = ["time", "close", "high", "low", "open"]


def transform(data):
    """ """

    data = _todate(data)

    data = data[COLS].copy()

    #     data = _trend_decreasing(data)

    return data
