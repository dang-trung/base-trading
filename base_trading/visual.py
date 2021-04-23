#!/usr/bin/env python3
"""
Make Plotly Figures

The script makes figures of asset prices with trading volumes, support lines, 
entry/exit prices, cumulative performance.
"""
import plotly.graph_objs as go
from plotly.subplots import make_subplots

colors = {
    'background': '#17171a',
    'text': '#ffffff',
    'buy': '#16c784',
    'sell': '#ea3943',
    'return': '#16c784'
}


def make_figure(data, ticker, scale="log", colors=colors):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.15, 0.15],
                        subplot_titles=['Price', 'Volume',
                                        'Portfolio Balance'])
    price = go.Scatter(x=data['Date'], y=data['Close'], name=ticker.upper(),
                       marker_color=colors['text'])

    fig.add_trace(price, row=1, col=1)
    trace_support = go.Scatter(x=data['Date'], y=data['Support Line'],
                               name='Support', mode='lines',
                               marker_color=colors['sell'], showlegend=False)
    fig.add_trace(trace_support, row=1, col=1)
    trace_buysignals = go.Scatter(x=data['Date'], y=data['Bought Price'],
                                  name='Buy', mode='markers',
                                  marker_color=colors['buy'],
                                  marker_symbol='triangle-up',
                                  marker_size=15)
    fig.add_trace(trace_buysignals, row=1, col=1)
    trace_sellsignals = go.Scatter(x=data['Date'], y=data['Sold Price'],
                                   name='Sell', mode='markers',
                                   marker_color=colors['sell'],
                                   marker_symbol='triangle-down',
                                   marker_size=15)
    fig.add_trace(trace_sellsignals)
    volume = go.Bar(x=data['Date'], y=data['Volume'], name='Volume',
                    opacity=1, marker_line_width=0,
                    marker_color=colors['text'],
                    showlegend=False)
    fig.add_trace(volume, row=2, col=1)
    trace_strat = go.Scatter(x=data['Date'], y=data['Base Trading'],
                             name='Strategy', mode='lines',
                             line_color=colors['return'], showlegend=False)
    fig.add_trace(trace_strat, row=3, col=1)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        bargap=0
    )

    fig.update_yaxes(type=scale, dtick=0.5, row=1, col=1, tickformat=".1f")
    fig.update_yaxes(rangemode="tozero", row=3, col=1)
    fig.update_xaxes(showgrid=False)

    return fig


if __name__ == '__main__':
    from .backtest import BaseTrader
    import pandas as pd

    ticker = 'BTC-USD'

    data = pd.read_csv(f'data/{ticker}.csv', index_col=0)
    base_trader = BaseTrader(break_support=0.2, break_resist=0.5, max_pos=10,
                             valid_days=10)
    data = base_trader.execute(data)

    import plotly.io as pio

    pio.renderers.default = "browser"
    fig = make_figure(data)
    fig.show()
