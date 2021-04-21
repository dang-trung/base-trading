"""
Backtest Base Trading Strategy

The script finds dates when prices are supported and computes entry/exit price
according to Base Trading strategy, as well as does backtesting and computes
additional performance stats of the strategy.
"""
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

    def __init__(self, price='Close', valid_days=50,
                 break_support=0.1, break_resist=0.1, max_pos=3):
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
        DataFrame
            Processed version of the input dataframe, with added columns:
            Support, Bought Price, Sold Price, Strategy Cumulative Returns,
            etc.
        """
        X_copy = X.copy()
        self._find_support(X_copy)
        self._make_support_line(X_copy)
        self._make_signal(X_copy)
        self._strat_return(X_copy)
        return X_copy

    # --------------------- Find Support Prices ---------------------
    # ASSUMPTIONS:
    # - Supports are the local lowest prices during a period of days (set in
    #   the begininng).
    # - When a support is broken, it's assumed to become new resistance
    #   (basic TA) and there's a chance that the price will visit that region
    #   near that support again.
    # - The longer the "period of support" gets, the stronger the supports are,
    #   the higher chance of price visiting the broken supports again.
    # - We trade this opportunity.

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
            today_pos = X.loc[i, 'Position'] = X.loc[i - 1, 'Position']
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

    def _strat_return(self, X):
        X['Market Return'] = np.log(X[self.price] / X[self.price].shift(1))
        X['Strategy Return'] = X['Position'].shift(1) * X['Market Return']
        X['Strategy'] = X['Strategy Return'].cumsum().apply(np.exp)
        X['Strategy'] = X['Strategy'] * 100


if __name__ == '__main__':
    import pandas as pd
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
    import plotly.io as pio

    pio.renderers.default = "browser"
    ticker = 'ETH-USD'

    data = pd.read_csv(f'data/{ticker}.csv', index_col=0)
    transformer = BaseTrader(break_support=0.2, break_resist=0.5, max_pos=10,
                             valid_days=10)
    data = transformer.execute(data)

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.15, 0.15],
                        subplot_titles=['Price', 'Volume',
                                        'Cumulative Returns'])
    price = go.Scatter(x=data['Date'], y=data['Close'], name=ticker.upper(),
                       marker_color='#ffffff')

    fig.add_trace(price, row=1, col=1)
    trace_support = go.Scatter(x=data['Date'], y=data['Support Line'],
                               name='Support', mode='lines',
                               marker_color='#ea3943', showlegend=False)
    fig.add_trace(trace_support, row=1, col=1)
    trace_buysignals = go.Scatter(x=data['Date'], y=data['Bought Price'],
                                  name='Buy', mode='markers',
                                  marker_color='#16c784',
                                  marker_symbol='triangle-up',
                                  marker_size=15)
    fig.add_trace(trace_buysignals, row=1, col=1)
    trace_sellsignals = go.Scatter(x=data['Date'], y=data['Sold Price'],
                                   name='Sell', mode='markers',
                                   marker_color='#ea3943',
                                   marker_symbol='triangle-down',
                                   marker_size=15)
    fig.add_trace(trace_sellsignals)
    volume = go.Bar(x=data['Date'], y=data['Volume'], name='Volume',
                    opacity=1, marker_line_width=0, marker_color='#ffffff',
                    showlegend=False)
    fig.add_trace(volume, row=2, col=1)
    colors = {
        'background': '#111111',
        'text': '#ffffff'
    }
    trace_strat = go.Scatter(x=data['Date'],
                             y=data['Strategy'][data['Strategy'] >= 1],
                             name='Strategy', mode='lines',
                             line_color='#16c784', showlegend=False)
    fig.add_trace(trace_strat, row=3, col=1)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        bargap=0
    )

    fig.update_yaxes(type="log", dtick=0.5, row=1, col=1, tickformat=".1f")
    fig.update_yaxes(rangemode="tozero", row=3, col=1)
    fig.update_xaxes(showgrid=False)
    fig.show()
