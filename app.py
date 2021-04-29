#!/usr/bin/env python3
"""
Dashboard App

The script creates a dashboard app providing the chart with entry/exit
positions and additional statistics on the strategy"s performance using
Plotly Dash.
"""
import os
from datetime import date
import time

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from base_trading.data import Collector, SourceNotSupported
from base_trading.backtest import BaseTrader
from base_trading.visual import make_figure, COLORS

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
app.title = 'Base Trading: Buy the Dip, Sell the Hype'
server = app.server

# -------------------------------- Navbar --------------------------------
LOGO_PATH = "https://raw.githubusercontent.com/dang-trung/base-trading/master" \
    "/assets/logo.png"

logo = dbc.Col(
    html.Img(src=LOGO_PATH, height="30px", style={
             "padding-left": "2em", "padding-right": "1em"}),
    width="auto"
)

brand = dbc.Col(
    dbc.NavbarBrand("Base Trading Backtester", style={"font-size": "1.4rem"}),
    width="auto"
)


dropdown = dbc.Col(
    dbc.DropdownMenu(
        label="More",
        children=[
            dbc.DropdownMenuItem(
                "Source Code", href="https://github.com/dang-trung/base-trading"
            ),
            dbc.DropdownMenuItem(
                "Feedback/Bug Report", href=f"mailto:dangtrung96@gmail.com"
            ),
        ],
    ),
    width={"offset": 7},
    style={"padding-left": "5em"}
)

navbar = html.Div(
    [
        dbc.Row(
            [logo, brand, dropdown],
            align="center", no_gutters=True
        ),
    ],
    # className="navbar navbar-expand-lg navbar-dark bg-dark",
    style={"background-color": "#1c1e22"}
)

# -------------------------------- App Settings --------------------------------

inputs = html.Div(
    [
        html.H2("Settings"),
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
                                      value=date(2016, 1, 1))
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
                                      value=date(2021, 4, 1))
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
                    dbc.Button("Submit", id="submit-button",
                               n_clicks=0, color="dark")
                ),
            ]
        )
    ],
    className="jumbotron",
)

# -------------------------------- App Outputs --------------------------------
price_graph = html.Div(
    [
        html.H2("Price & Signals"),
        html.P(),
        dbc.Spinner(html.Div(id="price-graph"))
    ],
    className="jumbotron"
)

strat_graph = html.Div(
    [
        html.H2("Portfolio Balance (Base Trading)"),
        html.P(),
        html.Div(id="strat-graph")
    ],
    className="jumbotron"
)

table = html.Div(
    [
        html.H2("Performance Comparison"),
        html.P(),
        html.Div(id="stats-table")
    ],
    className="jumbotron"
)

# ------------------------- Disclaimer, Footer, Instruction --------------------------------
disclaimer = html.Div(
    [
        html.H2("Disclaimer"),
        html.P(),
        html.Div(
            "This is just a fun project and NOT financial advice. As always, DYOR.")
    ],
    className="jumbotron"
)

MAIL_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/gmail-white.svg"
GITHUB_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/github-white.svg"
LINKEDIN_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/linkedin-white.svg"

footer = html.Div(
    [
        html.P(
            [
                "made by ",
                html.A(html.B("Trung Dang"),
                       href="https://dang-trung.github.io/"),
                ", 2020 ",
                html.Img(src=LOGO_PATH, height="30px",
                         style={"padding-right": "1rem"})
            ],
        ),
        html.P(
            [
                html.A(
                    html.Img(src=MAIL_ICON, height="30px",
                             style={"padding-right": "1rem"}),
                    href="mailto:dangtrung96@gmail.com"
                ),
                html.A(
                    html.Img(src=GITHUB_ICON, height="30px",
                             style={"padding-right": "1rem"}),
                    href="https://github.com/dang-trung"
                ),
                html.A(
                    html.Img(src=LINKEDIN_ICON, height="30px",
                             style={"padding-right": "1rem"}),
                    href="https://www.linkedin.com/in/dang-trung/"
                ),
            ]
        )
    ],
    style={"text-align": "center"}
)

collapse_button = dbc.Button(
    "Feeling Confused?",
    id="collapse-button",
    className="mb-3",
    color="primary",
)

instructions = html.Div(
    [
        html.H2("What Is Base Trading?"),
        html.P(),
        html.P('1. Support (or "Base") refers to the price level that an asset struggles to fall below over a given time period.'),
        html.P("2. Use"),
        html.P("3. Use"),
        html.H2("How To Use"),
        html.P(),
        html.P("1. Use"),
        html.P("2. Use"),
        html.P("3. Use"),
    ],
    className="jumbotron"
)
# ------------------------------ Final Layout --------------------------------

app.layout = html.Div(
    [
        navbar,
        html.P(),
        dbc.Container(
            [
                collapse_button,
                dbc.Collapse(
                    instructions,
                    id="collapse",
                ),
                # dbc.Row(dbc.Col(instructions)),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                price_graph,
                                strat_graph,
                                table
                            ], width=8
                        ),
                        dbc.Col(
                            [
                                inputs,
                                disclaimer
                            ]),
                    ]
                ),
            ],
        ),
        footer,
        html.P()
    ],
)


@app.callback(
    [
        Output("price-graph", "children"),
        Output("strat-graph", "children"),
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
    data_path = os.path.join("data", f"{ticker}.csv")
    break_support /= 100
    break_resist /= 100
    try:
        collector = Collector(ticker, source, start, end, data_path)
    except SourceNotSupported:
        error_message = dbc.Alert(
            "Sorry! Only Yahoo Finance is supported at the moment.",
            color="primary"
        )
        return error_message, error_message, error_message

    data = collector.get_historical()

    base_trader = BaseTrader(
        price, valid_days, break_support, break_resist, max_pos, init_cash)
    data, stats = base_trader.execute(data)

    figure, strat = make_figure(data, ticker, price, COLORS)

    figure = dcc.Graph(figure=figure)
    strat = dcc.Graph(figure=strat)
    stats = dbc.Table.from_dataframe(stats)

    if n_clicks:
        return figure, strat, stats
    return figure, strat, stats

    # load_output = dbc.Button(
    #     [
    #         dbc.Spinner(size="sm"),
    #         " Submit your inputs..."
    #     ],
    #     disabled=True,
    # )
    # return load_output, load_output, load_output


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(debug=True)
