#!/usr/bin/env python3
"""
Data Collector

This script allows fetching historical prices of assets available on Yahoo!
Finance and stored the data in csv files.

"""
import os

import pandas as pd
import pandas_datareader.data as web  # Reads stock data from Yahoo!


class Collector:
    """
    A class used to collect historical prices from the Yahoo! Finance
    database

    ...

    Attributes
    ----------
    ticker : str
        Asset ticker
    start : str
        Starting date in YYYY-MM-DD format
    end : str
        Ending date in YYYY-MM-DD format
    data_path : str
        Path to store the fetched data

    Methods
    ----------
    fetch()
        Fetch the historical data from the Yahoo! Finance database

    get_historical()
        Wrapper of fetch() to handle cases where data of the
        target asset has already been fetched before

    """

    def __init__(self, ticker, start, end, data_path):
        """
        Parameters
        ----------
        ticker : str
            Asset ticker, look up on Yahoo! Finance e.g. 'BTC-USD' for Bitcoin
        start : str
            Starting date in YYYY-MM-DD format
        end : str
            Ending date in YYYY-MM-DD format
        data_path : str
            Path to store the fetched data
        """
        self.ticker = ticker
        self.start = start
        self.end = end
        self.data_path = data_path

    def fetch(self):
        """
        Fetch the historical data from the Yahoo! Finance database into a
        DataFrame.
        Also stored the data in a .csv file.

        Returns
        -------
        DataFrame
            A DataFrame of historical prices fetched from Yahoo! Finance
        """
        try:
            data = web.DataReader(self.ticker, 'yahoo', self.start, self.end)
        except KeyError:
            raise NoTickerError(
                f"{self.ticker} not available on Yahoo! Finance.")
        data.reset_index(inplace=True)
        data.to_csv(self.data_path)
        return data

    def get_historical(self):
        """
        Wrapper of fetch() to handle cases where data of the
        target asset has already been fetched before

        Returns
        -------
            A DataFrame of historical prices fetched from Yahoo! Finance
        """
        if os.path.exists(self.data_path):
            data = pd.read_csv(self.data_path, index_col=0)
            first_date = data['Date'][0]
            if pd.to_datetime(first_date) > pd.to_datetime(self.start):
                data = self.fetch()
        else:
            data = self.fetch()
        return data


class NoTickerError(Exception):
    """
    Raised when the ticker is not available on Yahoo! Finance
    """
    pass


if __name__ == '__main__':
    start = '2016-01-01'
    end = '2021-01-01'
    ticker = 'ETH-USD'
    data_path = os.path.join('data', f'{ticker}.csv')

    collector = Collector(ticker, start, end, data_path)
    data = collector.get_historical()
    print(data.shape)
