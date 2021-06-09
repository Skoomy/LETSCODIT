import pandas as pd
import time
import click
from ripple import feature, utils, strategy, logger
import logging
import numpy as np

# logger = logging.getLogger(__name__)


def meta_setting(data, name="sample"):
    """ """
    if "time" not in data.columns:
        raise ValueError("date not in columns")

    result = {}
    result["start_period"] = data["time"].min().__str__()
    result["end_period"] = data["time"].max().__str__()
    result["nb_obs"] = data.shape[0]
    result["name"] = name

    return result


def load():
    data = pd.read_csv("data/XRP_price_20210608.csv")
    data["date"] = data["time"].apply(utils.to_date)
    return data


def run():
    data = load()
    data = feature.transform(data).dropna()

    df_down, result = feature._trend(data, "decreasing")
    df_down.to_csv("data/down_data.csv", index=False)
    result.to_csv("data/down_analysis.csv", index=False)

    # =======
    df_up, result = feature._trend(data, "increasing")
    result.to_csv("data/up_analysis.csv", index=False)
    df_up.to_csv("data/up_data.csv", index=False)

    settings = []
    xtest, xval, xtrain = utils.train_test_split(data)
    print(xtest)

    for (k, n) in zip([xtest, xval, xtrain], ["test", "val", "train"]):

        settings.append(meta_setting(data=k, name=n))

    #     xtest = feature._trend(xtest)
    settings = pd.DataFrame(settings)
    settings.to_csv("data/settings.csv", index=False)
    print(settings)

    return data


def run_strat(data, _cash=10, period=3, name="ripple_trend"):

    click.clear()

    click.secho("\t\t\t .....Starting computation ......\n", fg="green")
    logger.info("{} execution".format(run))
    tic = time.time()

    actif = strategy.runner(data=data, cash=_cash, name=name, period=period)

    pnl = actif.broker.getvalue() - _cash
    returns = np.round((actif.broker.getvalue() - _cash) / _cash, 4) * 100
    msg = "\n\t\tPNL {0}\n \t\tReturns : {1} % ".format(pnl, returns)
    click.secho(msg, fg="red")
    print("-" * 100)
    computation_time = time.time() - tic
    msg = "took {} ".format(computation_time)
    click.secho(msg, fg="green")
    return


if __name__ == "__main__":
    click.secho("Run Ripple", fg="green")
    data = load()
    data = data[data["date"] >= "2021-01-01"]
    data = data[data["date"] < "2021-05-01"]
    print(data.shape)
    _period = [4]
    for k in _period:
        run_strat(data.copy(), _cash=1000, period=k)
    # run()
