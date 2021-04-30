[![MIT License][license-shield]][license-url]
[![GitHub][github-shield]][github-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/dang-trung/base-trading">
    <img src="https://raw.githubusercontent.com/othneildrew/Best-README-Template/master/images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Base Trading Backtester</h3>
</p>
  <p align="center">
    A web application to backtest Base Trading Strategy
  </p>

## Introduction

* **Objective**: This app creates a dashboard using Dash to visualize and backtest base trading Strategy.

* **Status**: On Hold

## Features
- Supports all Yahoo! Finance tickers
- Allows to choose entry and exit patterns following base trading strategy
- Performs backtesting on selected signals automatically
- Visualizes prices, entries, exits, and portfolio value using Plotly
- Displays key performance metrics such as returns, volatility, Sharpe ratio, etc.
- Compares base trading with simple holding
- Responsive design using Dash Bootstrap Components

## Live Version
https://base-trading.herokuapp.com/

## Dependencies
* Python 3
* dash==1.13.3
* dash_bootstrap_components==0.12.0
* numpy==1.19.5
* pandas==1.2.1
* pandas-datareader==0.9.0
* plotly==4.14.3
* scipy==1.6.0
* gunicorn==20.0.4

## How to Run
1. Clone this repo:
`$ git clone https://github.com/dang-trung/base-trading`
1. Create your environment (virtualenv):  
`$ virtualenv -p python3 venv`  
`$ source venv/bin/activate` (bash) or `$ venv\Scripts\activate` (windows)   
`$ (venv) cd base-trading`  
`$ (venv) pip install -e`  
1. Run the app:  
`$ python app.py`

## Screenshot
![screenshot.png](https://raw.githubusercontent.com/dang-trung/base-trading/master/assets/screenshot.png)

## What Is Base Trading?
1. Support (or "Base") refers to the price level that an asset struggles to fall below over a given time period.

2. Usually, the longer this period is, the "stronger" (i.e. harder to be broken) the bases should be.

3. If we have an asset with a very bullish outlook in the long term, and some of its supports are broken today (e.g. in a panicked market), we expect (or at least assume) that these price levels will be re-visited eventually at a future date.

4. At this date, the previously broken supports will become resistances (an "S/R flip" in T/A terms) since many people who bought at the supports before will want to sell for break-evens.

5. We trade this opportunity. This means we buy where supports are broken for some pre-determined percentages (thus the term "buy the dip") and sell where broken supports are re-visited, or even better PENETRATED for some pre-determined percentages (e.g. in a hyped market).

6. To maximize returns/Sharpe/whatever your goals are with this strategy, our job is to optimized the parameters (or even the strategy itself if you can) and backtested them with the assets you'd like to trade. 

<!-- MARKDOWN LINKS & IMAGES -->
[github-shield]: https://img.shields.io/badge/-GitHub-black.svg?style=social&logo=github&colorB=555
[github-url]: https://github.com/dang-trung/
[license-shield]: https://img.shields.io/github/license/dang-trung/base-trading.svg?style=social
[license-url]: https://github.com/dang-trung/base-trading/blob/master/LICENSE.md
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=social&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/dang-trung
