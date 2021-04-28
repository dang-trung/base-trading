#!/usr/bin/env python3
"""
Dashboard App

The script creates a dashboard app providing the chart with entry/exit
positions and additional statistics on the strategy"s performance using
Plotly Dash.
"""
import os
from datetime import date

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from data import Collector, SourceNotSupported
from backtest import BaseTrader
from visual import make_figure

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SIMPLEX])
server = app.server

LOGO = "https://raw.githubusercontent.com/dang-trung/base-trading/master" \
       "/assets/logo.png"
navbar = dbc.Navbar(
    [
        dbc.Row(
            [
                dbc.Col(html.Img(
                    src=LOGO,
                    height="30px",
                    style={"padding-right": "1rem"}
                )
                ),
                dbc.Col(
                    dbc.NavbarBrand(
                        "Base Trader",
                        style={"font-size": "1.4rem"}
                    ),
                ),
                dbc.Col(
                    dbc.DropdownMenu(
                        label="See More",
                        children=[
                            dbc.DropdownMenuItem("Source Code",
                                                 href=f"https://github.com/"
                                                      "dang-trung/base-trading"
                                                 ),
                            dbc.DropdownMenuItem("Request",
                                                 href=f"mailto:dangtrung96"
                                                      "@gmail.com"),
                        ]
                    ),
                )
            ],
            align="center",
            no_gutters=True,
        ),
    ],
    className="navbar navbar-expand-lg fixed-top navbar-light bg-light",
)

inputs = html.Div(
    [
        html.H2("Settings", className="display-5"),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                "Data Source", addon_type="prepend",
                                className="nav-tabs"),
                            dbc.Select(
                                id="data-source",
                                options=[
                                    {"label": "Yahoo! Finance",
                                     "value": "yahoo"},
                                    {"label": "Kucoin", "value": "kucoin"},
                                    {"label": "Binance", "value": "binance"}
                                ],
                                value="yahoo"
                            )
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                "Asset Ticker", addon_type="prepend"),
                            dbc.Input(id="ticker", type="text",
                                      value="BTC-USD")
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                "Start Date", addon_type="prepend"),
                            dbc.Input(id="start-date", type="date",
                                      value=date(2010, 1, 1))
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                "End Date", addon_type="prepend"),
                            dbc.Input(id="end-date", type="date",
                                      value=date(2020, 4, 1))
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon(
                                "Marked Price", addon_type="prepend"),
                            dbc.Select(
                                id="marked-price",
                                options=[
                                    {"label": "Open", "value": "Open"},
                                    {"label": "Close", "value": "Close"},
                                    {"label": "High", "value": "High"},
                                    {"label": "Low", "value": "Low"}
                                ],
                                value="Close")
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Initial Cash ($)"),
                            dbc.Input(id="init-cash",
                                      type="number", value=10000)
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Maximum # of Positions"),
                            dbc.Input(id="max-pos", type="number", value=5)
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Support in (Days)"),
                            dbc.Input(id="valid-days", type="number", value=20)
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Drop from Support (%)"),
                            dbc.Input(id="break-support",
                                      type="number", value=10)
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.InputGroup(
                        [
                            dbc.InputGroupAddon("Break from Support (%)"),
                            dbc.Input(id="break-resist",
                                      type="number", value=40)
                        ]
                    )
                ),
            ]
        ),
        html.P(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button("Submit", id="submit-button", n_clicks=0)
                ),
            ]
        )
    ],
    className="jumbotron",
)

graph = html.Div(
    [
        html.H2("Price & Signals", className="display-5"),
        html.P(),
        html.Div(id="price-graph")
    ],
    className="jumbotron"
)

table = html.Div(
    [
        html.H2("Performance", className="display-5"),
        html.P(),
        html.Div(id="stats-table")
    ],
    className="jumbotron"
)

disclaimer = html.Div(
    [
        html.H2("Disclaimer", className="display-5"),
        html.P(),
        html.Div("This is a fun project only. No financial advises. DYOR.")
    ],
    className="jumbotron"
)

app.layout = dbc.Container(
    [
        navbar,
        html.P(),
        dbc.Row(
            [
                dbc.Col(graph, width=8),
                dbc.Col(inputs, width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(table, width=8),
                dbc.Col(disclaimer, width=4)
            ]
        ),
    ],
    style={"padding": "2em"}
)


@app.callback(
    [
        Output("price-graph", "children"),
        Output("stats-table", "children"),
    ],
    [
        Input("submit-button", "n_clicks"),
    ],
    [
        State("ticker", "value"),
        State("data-source", "value"),
        State("start-date", "value"),
        State("end-date", "value"),
        State("marked-price", "value"),
        State("init-cash", "value"),
        State("max-pos", "value"),
        State("valid-days", "value"),
        State("break-support", "value"),
        State("break-resist", "value"),
    ]
)
def update_strat(n_clicks, ticker, source, start, end, price, init_cash,
                 max_pos, valid_days, break_support, break_resist):
    colors = {
        'background': None,
        'text': None,
        'buy': '#16c784',
        'sell': '#ea3943',
        'return': '#16c784'
    }
    if n_clicks:
        data_path = os.path.join("data", f"{ticker}.csv")
        break_support /= 100
        break_resist /= 100
        try:
            collector = Collector(ticker, source, start, end, data_path)
        except SourceNotSupported:
            error_message = dbc.Alert(
                "Sorry! Only Yahoo! Finance is supported at the moment.",
                color="primary")
            return error_message, error_message

        data = collector.get_historical()

        base_trader = BaseTrader(
            price, valid_days, break_support, break_resist, max_pos, init_cash)
        data, stats = base_trader.execute(data)

        figure = make_figure(data, ticker, colors=colors)

        figure = dcc.Graph(figure=figure)
        stats = dbc.Table.from_dataframe(stats)

        return figure, stats
    else:
        load_output = dbc.Button(
            [
                dbc.Spinner(size="sm"),
                " Submit your inputs..."
            ],
            color="primary",
            disabled=True,
        )
        return load_output, load_output


if __name__ == '__main__':
    app.run_server(debug=True)
