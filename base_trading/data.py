#!/usr/bin/env python3
"""
Data Collector

The script allows fetching historical prices of assets available on Yahoo!
Finance and storing the data in csv files.
"""
import os

import pandas as pd
import pandas_datareader.data as web  # Reads stock data from Yahoo!


class Collector:
    """
    A class used to collect historical prices from the Yahoo! Finance
    database

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

    def __init__(self, ticker, source, start, end, data_path):
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
        self.source = source
        if self.source != "yahoo":
            raise SourceNotSupported(
                "Only Yahoo! Finance is supported at the moment.")
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
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
            data = web.DataReader(self.ticker, self.source, self.start,
                                  self.end)
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
            data['Date'] = pd.to_datetime(data['Date'])
            first_date, end_date = data.iloc[0, 0], data.iloc[-1, 0]

            # Fetch new data if we do not have the dates required on our
            # cache yet
            if first_date > self.start or end_date < self.end:
                data = self.fetch()
            # Or simply filter to avoid calling the API again
            else:
                mask = (self.start < data['Date']) & (data['Date'] < self.end)
                data = data[mask]
                data.reset_index(drop=True, inplace=True)
        else:
            data = self.fetch()
        return data


class NoTickerError(Exception):
    """
    Raised when the ticker is not available on Yahoo! Finance
    """
    pass


class SourceNotSupported(Exception):
    """
    Raised when the data source is unsupported
    """
    pass