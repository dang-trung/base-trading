#!/usr/bin/env python3
"""
Backtest Base Trading Strategy

The script finds dates when prices are supported and computes entry/exit price
according to Base Trading strategy, as well as does backtesting and computes
additional performance stats of the strategy.
"""
import pandas as pd
import numpy as np
from scipy.signal import argrelextrema


class BaseTrader:
    """
    A class used to find supports, compute entry/exit prices and backtest
    the strategy.

    Methods
    ----------
    execute()
        Wrapper that does everything in bulk (find supports, compute
        entry/exit prices and backtest)
    """

    def __init__(self, price, valid_days=20,
                 break_support=0.1, break_resist=0.4, max_pos=5,
                 init_cash=10000):
        """
        Parameters
        ----------
        price : {"Open", "Close", "High", "Low"}, default="Close"
            Prices to be used for backtesting
        valid_days : int or float, default=50
            Number of days a local support should stay valid in order to be
            considered a true support
        break_support : float, default=0.1
            % Drop from a support to start an entry position
        break_resist : float, default=0.1
            % Penetrate from a support (previously used to make an entry) to
            exit the position
        """
        self.price = price
        self.valid_days = valid_days
        self.dip_to_buy = 1 - break_support
        self.hype_to_sell = 1 + break_resist
        self.max_pos = max_pos
        self.pos_size = 1 / max_pos
        self.init_cash = init_cash

    def execute(self, X):
        """
        Wrapper that does everything in bulk (find supports, compute
        entry/exit prices, backtest)

        Parameters
        ----------
        X : DataFrame
            Contains the asset's historical prices.

        Returns
        -------
        X_copy : DataFrame
            Processed version of the input dataframe, with added columns:
            Support, Bought Price, Sold Price, Strategy Cumulative Returns,
            etc.

        stats : DataFrame
            Contains performance metrics of Base Trading compared to a
            simple Buy-and-Hold strategy.
        """
        X_copy = X.copy()
        self._find_support(X_copy)
        self._make_support_line(X_copy)
        self._make_signal(X_copy)
        self._strat_return(X_copy)
        stats = self._simulate(X_copy)
        return X_copy, stats

    # --------------------- Find Support Prices ---------------------
    # ASSUMPTIONS:
    # - Supports are the local lowest prices during a period of days (set in
    #   the begininng).
    # - The longer the "period of support" gets, the stronger the supports are,
    #   the higher chance of price visiting the broken supports again.

    def _find_support(self, X):
        sup_ix = argrelextrema(X[self.price].values, np.less_equal,
                               order=self.valid_days)
        sup_prices = X.loc[sup_ix, self.price]
        X['Support'] = sup_prices

        self.sup_prices, self.sup_ix = [], []
        self.sup_prices = list(sup_prices[::-1])  # stored as stacks
        self.sup_ix = list(sup_ix[0][::-1])  # stored as stacks

    def _make_support_line(self, X):
        line_len = self.valid_days
        X["Support Line"] = X["Support"].fillna(method='ffill', limit=line_len)
        X["Support Line"].fillna(method='bfill', limit=line_len, inplace=True)

    # --------------------- Buy & Sell Signals ---------------------
    # RULES:
    # - Buy when prices are below (`Support * self.dip_to_buy`)
    # - Sell when prices are above (`Bought Support * self.hype_to_sell`)
    # - Start buying as prices drop from the largest supports to the
    #   smallest ones
    # - Can only keep buying if number of positions do not exceed the
    #   maximum (set in the begining)

    def _make_signal(self, X):
        today_sups, bought_sups = [], []  # store as stacks
        X.loc[0, 'Position'] = 0
        for i in range(1, len(X)):
            if len(self.sup_ix) > 0 and i > self.sup_ix[-1]:
                today_sups.append(self.sup_prices.pop())
                self.sup_ix.pop()
                today_sups.sort()
                # sort so we start buying when largest supports are broken

            # mimic yesterday's position in case there's no buys/sells today
            X.loc[i, 'Position'] = X.loc[i - 1, 'Position']
            today_price = X.loc[i, self.price]

            if (len(today_sups) > 0
                    and len(bought_sups) < self.max_pos
                    and today_price < today_sups[-1] * self.dip_to_buy):
                X.loc[i, 'Position'] += self.pos_size
                X.loc[i, 'Bought Price'] = today_price
                bought_sups.append(today_sups.pop())

            if (len(bought_sups) > 0
                    and today_price > bought_sups[0] * self.hype_to_sell):
                X.loc[i, 'Position'] -= self.pos_size
                X.loc[i, 'Sold Price'] = today_price
                bought_sups = bought_sups[1:]

    # --------------------- Compute Cumulative Returns  ---------------------
    def _strat_return(self, X):
        X['Market Log Return'] = np.log(X[self.price] / X[self.price].shift(1))
        X['Strategy Log Return'] = X['Position'].shift(1) * X[
            'Market Log Return']
        X['Buy & Hold'] = (X['Market Log Return'].cumsum().apply(np.exp)
                           * self.init_cash)
        X['Base Trading'] = (X['Strategy Log Return'].cumsum().apply(np.exp)
                             * self.init_cash)
        X['Market Return'] = ((X['Buy & Hold'] - X['Buy & Hold'].shift(1))
                              / X['Buy & Hold'])
        X['Strategy Return'] = (
                (X['Base Trading'] - X['Base Trading'].shift(1))
                / X['Base Trading'])

    def _simulate(self, X):
        stats = pd.DataFrame(index=["Buy & Hold", "Base Trading"])
        n = len(X) - 1
        stats["Start"] = X.loc[0, "Date"]
        stats["End"] = X.loc[n, "Date"]
        stats["Duration"] = (stats["End"] - stats["Start"]).apply(
            lambda x: f"{x.days} days")
        stats["Initial Cash"] = self.init_cash

        for strategy in ["Buy & Hold", "Base Trading"]:
            stats.loc[strategy, "Ending Cash"] = X.loc[n, strategy]

        stats["Total Profit"] = stats["Ending Cash"] - stats["Initial Cash"]
        stats["Profit Margin (%)"] = (stats["Total Profit"] /
                                      stats["Initial Cash"] * 100)
        stats["Profit Margin (%)"] = stats["Profit Margin (%)"].apply(
            lambda x: f"{int(x):,}% ({round(x / 100, 2)}x)")
        stats["Initial Cash"] = stats["Initial Cash"].apply(
            lambda x: f"${x:,}")
        stats["Ending Cash"] = stats["Ending Cash"].apply(
            lambda x: f"${int(x):,}")
        stats["Total Profit"] = stats["Total Profit"].apply(
            lambda x: f"${int(x):,}")
        stats.loc["Buy & Hold", "Annualized Return (%)"] = np.average(
            X["Market Return"][2:])
        stats.loc["Base Trading", "Annualized Return (%)"] = np.average(
            X["Strategy Return"][2:])
        stats["Annualized Return (%)"] = ((stats[
                                               "Annualized Return (%)"] + 1)
                                          ** 365 - 1) * 100
        stats.loc["Buy & Hold", "Annualized Volatility (%)"] = np.std(
            X["Market Return"][2:])
        stats.loc["Base Trading", "Annualized Volatility (%)"] = np.std(
            X["Strategy Return"][2:])
        stats["Annualized Volatility (%)"] = (stats[
            "Annualized Volatility (%)"]) * np.sqrt(365) * 100
        stats["Sharpe Ratio"] = ((stats["Annualized Return (%)"] - 0.08) /
                                 stats["Annualized Volatility (%)"])
        stats["Annualized Return (%)"] = stats["Annualized Return (%)"].apply(
            lambda x: f"{round(x, 2)}%")
        stats["Annualized Volatility (%)"] = stats[
            "Annualized Volatility (%)"].apply(lambda x: f"{round(x, 2)}%")
        stats["Sharpe Ratio"] = stats["Sharpe Ratio"].apply(
            lambda x: round(x, 2))

        stats = stats.T.reset_index()
        stats.rename(columns={"index": "Metrics"}, inplace=True)
        return stats
