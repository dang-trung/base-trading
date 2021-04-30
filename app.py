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
from dash_html_components.A import A

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
        in_navbar=True
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
                                      value=date(2018, 1, 1))
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
                                      value=date(2021, 1, 1))
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
        dbc.Spinner(html.Div(id="price-graph")),
    ],
    className="jumbotron"
)

strat_graph = html.Div(
    [
        html.H2("Portfolio Balance (Base Trading)"),
        html.P(),
        dbc.Spinner(html.Div(id="strat-graph"))
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

# ------------------------- Footer, Instruction -------------------------------

MAIL_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/gmail-white.svg"
GITHUB_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/github-white.svg"
LINKEDIN_ICON = "https://raw.githubusercontent.com/dang-trung/base-trading/692aba3c5db2bb655feda2e497918193a1a6b496/assets/linkedin-white.svg"

footer = html.Div(
    [
        html.P(
            [
                "made by ",
                html.A(html.B("Trung Dang"),
                       href="https://dang-trung.github.io/",
                       style={"text-decoration": "underline"}),
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
    style={
        "background-image": "linear-gradient(#1c1e22, #1c1e22 60%, #1c1e22)"
    }
)

instructions = html.Div(
    [
        html.H2("What Is Base Trading?"),
        html.P(),
        html.P('1. Support (or "Base") refers to the price level that an asset struggles to fall below over a given time period.'),
        html.P('2. Usually, the longer this period is, the "stronger" (i.e. harder to be broken) the bases should be.'),
        html.P("3. If we have an asset with a very bullish outlook in the long term, and some of its supports are broken today (e.g. in a panicked market), we expect (or at least assume) that these price levels will be re-visited eventually at a future date. "),
        html.P('4. At this date, the previously broken supports will become resistances (an "S/R flip" in T/A terms) since many people who bought at the supports before will want to sell for break-evens.'),
        html.P('5. We trade this opportunity. This means we buy where supports are broken for some pre-determined percentages (thus the term "buy the dip") and sell where broken supports are re-visited, or even better  PENETRATED for some pre-determined percentages (e.g. in a hyped market).'),
        html.P("6. To maximize returns/Sharpe/whatever your goals are with this strategy, our job is to optimized the parameters (or even the strategy itself if you can) and backtested them with the assets you'd like to trade. "),
        html.H2("How Do I Start?"),
        html.P(),
        html.P(["1. Choose a data source (for now only Yahoo! Finance). The app supports any asset ticker that could be found on their ", html.B(html.A("site.", href="https://finance.yahoo.com/", style={"text-decoration": "underline"}))]),
        html.P("2. Dates and marked prices are trivially explained."),
        html.P("3. Next, set up the initial cash for your simulated portfolio using this strategy. Maximum # of Positions is how many long positions you could enter at most at the same time. Every time you sell, your available number of positions will be refilled."),
        html.P('4. "Support in (Days)" determines how "strong" your bases are.'),
        html.P("5. For the last two parameters, you buy when the price drops below any support by the first percentage, and sell when it gets back up and penetrates the previously broken support by the latter percentage."),
        html.P("6. Submit to see results."),
        html.H2("What Could Possibly Turn Wrong? "),
        html.P(),
        html.P("1. As always, past performance is no guarantee of future results. If you seriously want to backtest a strategy, find a sampling scheme that avoids overfitting the data (e.g. you use the historical prices between 2017 and 2019, and your parameters work damn well during this time, but it gets outperformed badly by the hodling strat during 2020 and 2021. This is overfitting.)"),
        html.P("2. Mathematically speaking, returns/Sharpe/etc. are merely functions of all parameters you provided, and it is possible that you can find the parameters to optimize those target variables (at least locally). In practice, however, for some markets with meteoric rises like BTC, although it is still possible to find the parameters to outperform the Hodling strategy, it is SUPER hard to do so."),
        html.H2("How Will This Dashboard Help Actually?"),
        html.P(),
        html.P("1. This dashboard helps you play around with the parameters to get a sense of how the strategy would turn out versus a simple Hodling strategy."),
        html.P("2. From my experiences, base trading works best during bear markets or at the beginning of bull ones. So you may use this during those times."),
        html.P("3. You can even use it to find very good entries for your Hodling positions and avoid buying local tops (which's gonna hurt your soul for a long time)."),
        html.H2("Last Notes"),
        html.P(),
        html.P("1. The dashboard is only a fun project and not financial advice. If you truly want to mimic the entries/exits with real money, do it at your own risk."),
        html.P("2. Feel free to contact me if you have some advice for UI improvements or other features."),
        html.P("3. If you have great fun playing around, a donation is always appreciated!"),
        html.P(
            "My ETH address: 0x310E736149d6EDEbE97a27619d617f901FE6626C", 
            style={"text-align": "center"},
        )
    ],
    className="jumbotron",
    style={"text-align": "justify"},
)
# ------------------------------ Final Layout --------------------------------

app.layout = html.Div(
    [
        navbar,
        html.P(),
        html.Div(
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
                            ]),
                    ]
                ),
            ],
            style={
                "padding-left": "2em",
                "padding-right": "2em",
            }
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
