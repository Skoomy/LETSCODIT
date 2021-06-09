import backtrader as bt
from ripple import utils, logger
import numpy as np

# import logging

# --------------------------------
# RSI isn't oversold too and below 50 area...


def stricly_decreasing(series, n):
    a = all([i > j for i, j in zip(series[-n:], series[1:])])
    return a


class Dummy(bt.Strategy):
    """A strategy based on trend ie The trend is your friend"""

    params = (
        # ("n_positions", 10),
        # ("min_positions", 5),
        ("period", 5),
        ("stop_loss", 0.03),  # price is 2% less than entry poitn
        ("verbose", False),
        ("trail", True),
        ("log_file", "backtest.csv"),
    )

    # ======================
    def __init__(self):
        super().__init__()
        # self.data_close = self.datas[0].close
        # self.data_open = self.datas[0].open
        # self.data_high = self.datas[0].high
        # self.data_low = self.datas[0].low

        self.pct_change = bt.ind.PctChange(period=self.p.period)
        # ===================================
        self.today = None
        #
        # be careful return n and not (n-1)
        self.min_val_period = bt.ind.MinN(
            self.data.close, period=self.p.period, plot=True
        )
        self.max_val_period = bt.ind.MaxN(
            self.data.close, period=self.p.period, plot=True
        )
        # doesn't try and do anything until it has p period of data
        self.addminperiod(self.p.period)

        self.order = None
        self.price = None
        self.comm = None
        self.profit = 0
        # ============
        self.buyvalue = 0
        self.buyprice = 0
        self.opsize = 0

    # =============================
    def _signal(self):
        """ """
        period = self.p.period
        res = []

        for i in range(-(period), 0):
            res.append(self.data_close[i])

        n = len(res)
        buy = all([i >= j for i, j in zip(res[-n:], res[1:])])
        if buy:
            return "buy"
        sell = all([i <= j for i, j in zip(res[-n:], res[1:])])
        if sell:

            return "sell"
        return "other"

    def max_n_1(self):
        """
        buy if close price above last n days
        """
        # range_total = 0
        period = self.p.period
        res = []
        for i in range(-(period), 0):
            res.append(self.data_close[i])

        avg = np.mean(res)

        return np.max(res)

    def min_n_1(self):
        """
        sell if close price below last n days
        """
        period = self.p.period
        res = []
        for i in range(-(period), 0):
            res.append(self.data_close[i])
        avg = np.mean(res)
        _min = np.min(res)
        return _min

    # =====================
    def log(self, msg):
        date = self.datas[0].datetime.date().isoformat()
        logger.info(msg)
        return msg

    def notify_trade(self, trade):
        """reporting the results of trades  after position are closed"""
        dt = trade.data.datetime.datetime()
        dn = trade.data._name
        if not trade.isclosed:
            return
        msg = "operation result gross: {} | Net: {}".format(trade.pnl, trade.pnlcomm)
        # self.log(msg)

        return

    def next(self):
        # self.log(
        #     "Next %0.2f, %0.2f, %0.2f, %0.2f"
        #     % (
        #         self.data.open[0],
        #         self.data.high[0],
        #         self.data.low[0],
        #         self.data.close[0],
        #     )
        # )
        pass

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        if order.status == order.Cancelled:
            print(
                "CANCEL@price: {:.2f} {}".format(
                    order.executed.price, "buy" if order.isbuy() else "sell"
                )
            )
            return

        if order.status in [order.Completed]:
            dt = bt.num2date(order.executed.dt).date()
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buyvalue = order.executed.value
                self.opsize = order.executed.size
                # dt = self.data.datetime.date().isoformat()
                # dt = bt.num2date(order.executed.dt).date()
                a = self.buyprice * self.opsize
                print("-" * 32, " NOTIFY TRADE ", "-" * 32)
                self.log(
                    f"{dt} Buy Executed --- Price: {self.buyprice:.2f} | Comm: {self.buycomm} | Cost: {order.executed.value:.2f}  Size: {order.executed.size}"
                )
                print("-" * 32, " £££ ", "-" * 32)
            if order.issell():
                gross_pnl = (order.executed.price - self.buyprice) * self.opsize
                msg = f"{dt} Sell Executed --- Price:{order.executed.price:.2f}, Cost: {order.executed.value:.2f} Commission: {order.executed.comm:.2f}"
                self.log(msg)

    # =================
    def update_profit(self):
        """update profit"""
        self.profit = 0
        if self.buyprice > 0:
            self.profit = np.float64(self.data.close[0] - self.buyprice) / self.buyprice
            # print(self.profit)
            return

    # =================
    def next_open(self):
        """
        Contains all the logic
        use if cheat-on-open is True
        """
        # self.log(
        #     "Next Open %0.2f, %0.2f, %0.2f, %0.2f"
        #     % (
        #         self.data.open[0],
        #         self.data.high[0],
        #         self.data.low[0],
        #         self.data.close[0],
        #     )
        # )
        # stop Loss
        # self.update_profit()
        _price_close = self.data_close[0]

        if not self.position:  # out of the market
            # compute signal
            _max_val = self.max_n_1()
            # signal = self._signal()

            if _price_close >= _max_val:
                # buy at the next open
                size = int(self.broker.getcash() / self.datas[0].open)
                self.order = self.buy(
                    data=self.datas[0], coo=True, coc=False, size=size
                )

            # if not self.p.trail:
            #     stop_price = _price_close * (1.0 - self.p.stop_loss)
            #     self.sell(exectype=bt.Order.Stop, price=stop_price)
            # else:
            #     pass
            # self.sell(exceptype=bt.Order.StopTrail, trailamount=self.p.trail)

            # self.log(
            #     "{0} Buy Send: {1} | OPEN : {2}-------- CLOSE {3}".format(
            #         self.datas[0].datetime.date().isoformat(),
            #         size,
            #         self.data.open[0],
            #         _price_close,
            #     )
            # )
        elif self.position:
            # check stop loss

            # if self.profit < self.p.stop_loss:
            #     self.log("STOP LOSS: current  percentage %.3f %%" % self.profit)
            #     self.order = self.sell(size=self.position.size)
            #     pass
            # else:
            if not self.p.trail:
                stop_price = _price_close * (1.0 - self.p.stop_loss)
                self.sell(exectype=bt.Order.Stop, price=stop_price)

            else:
                _min_val = self.min_n_1()
                signal = self._signal()
                if _min_val >= _price_close:
                    # generate sell order
                    msg = f"SELL @price ticket: {self.data_close[0]} | {self.position.size}"
                    self.log(msg)
                    self.order = self.sell(size=self.position.size)
                    # self.order = self.close()


def getpyfolio(result, name="backtrader"):
    # prepare pyfolio inputs
    pyfolio_analyzer = result[0].analyzers.getbyname("pyfolio")
    returns, positions, transactions, gross_lev = pyfolio_analyzer.get_pf_items()
    returns.to_hdf(f"{name}.h5", "returns")

    positions.to_hdf(f"{name}.h5", "positions")
    transactions.to_hdf(f"{name}.h5", "transactions/")
    gross_lev.to_hdf(f"{name}.h5", "gross_lev")
    return


# =============================================
def runner(data, cash, name, commission=0.015, period=5, fromdate=None, todate=None):

    data = utils._formatpandas(data=data, fromdate=fromdate, todate=todate)

    cerebro = bt.Cerebro(stdstats=False, cheat_on_open=True)

    cerebro.addstrategy(Dummy, period=period, log_file=f"{name}_log.csv", verbose=True)
    cerebro.adddata(data)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(
        commission=commission,
        commtype=bt.comminfo.CommInfoBase.COMM_FIXED,
        # stocklike=True,
    )
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)

    # =====
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="time_return")
    cerebro.addwriter(bt.WriterFile, out=f"{name}_result.csv", csv=True)

    msg = "Starting Portfolio Value: %.2f" % cerebro.broker.getvalue()
    logger.info(msg)
    results = cerebro.run(maxcpus=1)
    # getpyfolio(results, name=name)
    # extract pyfolio
    return cerebro
