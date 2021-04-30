#!/usr/bin/env python3
"""
Make Plotly Figures

The script makes figures of asset prices with trading volumes, support lines, 
entry/exit prices, cumulative performance.
"""
import plotly.graph_objs as go
from plotly.subplots import make_subplots

COLORS = {
    'background': None,
    'text': '#ffffff',
    'buy': '#16c784',
    'sell': '#ea3943',
    'return': '#16c784'
}
    
def make_figure(data, ticker, price, colors, scale="log"):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3],
                        subplot_titles=[ticker.upper(), 'Trading Volume'])
    price = go.Scatter(x=data['Date'], y=data[price], name=ticker.upper(), showlegend=False, marker_color=colors['text'])
    fig.add_trace(price, row=1, col=1)

    trace_support = go.Scatter(x=data['Date'], y=data['Support Line'], mode='lines', showlegend=False,                             marker_color=colors['sell'])
    fig.add_trace(trace_support, row=1, col=1)
    
    try:
        trace_buysignals = go.Scatter(x=data['Date'], y=data['Bought Price'],
                                    name='Buy', mode='markers',
                                    marker_color=colors['buy'],
                                    marker_symbol='triangle-up',
                                    marker_size=15)
        fig.add_trace(trace_buysignals, row=1, col=1)
    except KeyError:
        print("No base broken.")
    
    try:
        trace_sellsignals = go.Scatter(x=data['Date'], y=data['Sold Price'],
                                    name='Sell', mode='markers',
                                    marker_color=colors['sell'],
                                    marker_symbol='triangle-down',
                                    marker_size=15)
        fig.add_trace(trace_sellsignals)
    except KeyError:
        print("No sell has been made. HODLING.")

    volume = go.Bar(x=data['Date'], y=data['Volume'], name='Volume',
                    opacity=1, marker_line_width=0, marker_color=colors['text'],
                    showlegend=False)
    fig.add_trace(volume, row=2, col=1)

    fig.update_yaxes(type=scale, dtick=0.5, row=1, col=1, tickformat=".3f")

    trace_strat = go.Scatter(x=data['Date'], y=data['Base Trading'], mode='lines', showlegend=False, marker_color=colors['text'])
    strat = go.Figure(data=[trace_strat])
    strat.update_yaxes(rangemode="tozero", showgrid=False)

    for figure in [fig, strat]:
        figure.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)', 
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font_color=colors['text']
        )
        figure.update_xaxes(showgrid=False, showline=True, automargin=True)
        figure.update_yaxes(showline=True, automargin=True)

    return fig, strat

