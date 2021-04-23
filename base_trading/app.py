#!/usr/bin/env python3
"""
Dashboard App

The script creates a dashboard app providing the chart with entry/exit
positions and additional statistics on the strategy"s performance using
Plotly Dash.
"""
import plotly.graph_objs as go
import os
from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Output, Input

from data import Collector
from backtest import BaseTrader
from visual import make_figure

app = dash.Dash(__name__)
app.title = "Base Trader: Sell the Dip - Buy the Hype!"

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            children=[
                html.H1(
                    children="💸 Backtesting Base Trader"
                ),
                html.P(
                    children="Buy the Dip, Sell the Hype"
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Data Source"
                ),
                dcc.Dropdown(
                    id="data-source-dropdown",
                    options=[
                        {"label": "Yahoo! Finance", "value": "yahoo"},
                        {"label": "Kucoin", "value": "kucoin"},
                        {"label": "Binance", "value": "binance"}
                    ],
                    value="yahoo"
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Ticker"
                ),
                dcc.Input(
                    id="ticker-input",
                    type="text",
                    value="BTC-USD"
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Date Range"
                ),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=date(2016, 1, 1),
                    end_date=date(2021, 4, 20)
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Price Used to Find Supports"
                ),
                dcc.Dropdown(
                    id="price-used-dropdown",
                    options=[
                        {"label": "Open", "value": "Open"},
                        {"label": "Close", "value": "Close"},
                        {"label": "High", "value": "High"},
                        {"label": "Low", "value": "Low"}
                    ],
                    value="Close"
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Number Of Positions Allowed"
                ),
                dcc.Input(
                    id="max-pos-allowed",
                    type="number",
                    value=5
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Support Valid In (Days):"
                ),
                dcc.Input(
                    id="valid-days",
                    type="number",
                    value=20
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Initial Cash"
                ),
                dcc.Input(
                    id="init-cash",
                    type="number",
                    value=10000
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Dip (% Drop From Support)"
                ),
                dcc.Input(
                    id="dip-to-buy",
                    type="number",
                    value=10
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Hype (% Break From Support)"
                ),
                dcc.Input(
                    id="hype-to-sell",
                    type="number",
                    value=40
                )
            ]
        ),

        html.Div(
            children=[
                html.Div(
                    children="Figure"
                ),
                dcc.Graph(
                    id="price-figure"
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children="Strategy Performance"
                ),
                dash_table.DataTable(
                    id="stats-table"
                )
            ]
        )
    ],
)


@app.callback(
    [
        Output("price-figure", "figure"),
        Output("stats-table", "data"),
        Output("stats-table", "columns")
    ],
    [
        Input("ticker-input", "value"),
        Input("data-source-dropdown", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("price-used-dropdown", "value"),
        Input("valid-days", "value"),
        Input("dip-to-buy", "value"),
        Input("hype-to-sell", "value"),
        Input("init-cash", "value"),
        Input("max-pos-allowed", "value")
    ]
)
def simulate_strat(ticker, source, start, end, price, valid_days,
                   break_support, break_resist, init_cash, max_pos):
    # Convert parameters to appropriate format
    data_path = os.path.join("data", f"{ticker}.csv")
    break_support /= 100
    break_resist /= 100

    # Fetch asset prices from source
    if source == "yahoo":
        collector = Collector(ticker, start, end, data_path)
        data = collector.get_historical()

    # Add supports, entry/exit prices, cumulative returns
    base_trader = BaseTrader(price, valid_days, break_support,
                             break_resist, max_pos, init_cash)
    data, stats = base_trader.execute(data)
    # Make figures
    figure = make_figure(data, ticker)
    stats_dict = stats.to_dict("records")
    stats_col = [{"name": i, "id": i} for i in stats.columns]
    return figure, stats_dict, stats_col


if __name__ == "__main__":
    app.run_server(debug=True)
