import os
from glob import glob
import numpy as np
import pandas as pd


def read_data(directory):
    """
    Read stocks. Keeps only stocks whose all-time lowest low appears earlier than the highest high
    :param directory: The directory with the stock files.
    :return: stocks: Dictionary with stock names as keys and the pd series as values (indexed by date)
            stocks_min_max: Dataframe of stocks with their all-time min and max values (indexed by date)
            date_range: All days from start to end
    """
    print("Reading data...")
    files = glob(os.path.join(directory, '*.txt'))
    stock_names = [f.split("\\")[1].split('.')[0].upper() for f in files]

    # read stocks
    stocks = {}  # dictionary with stock names as keys and the pd series as values (indexed py date)
    values = []  # min max values
    for f, s in zip(files, stock_names):
        if os.path.getsize(f) > 0:  # a few files are empty
            stock = pd.read_csv(f, usecols=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
            stock['Date'] = pd.to_datetime(stock['Date']).dt.date
            stock = stock.set_index('Date')

            # don't consider stocks with their all-time min appearing later than the all-time max
            #  or those that have max - min < 1
            min_value = np.min(stock['Low'])
            max_value = np.max(stock['High'])
            min_date = stock['Low'].idxmin()
            max_date = stock['High'].idxmax()
            min_volume = stock['Volume'].loc[[min_date]].values[0]
            max_volume = stock['Volume'].loc[[max_date]].values[0]
            profit = max_value - min_value
            if min_date < max_date and profit >= 1:
                values.append([min_date, min_value, min_volume, max_date, max_value, max_volume, profit])
                stocks[s] = stock

    # contains stocks with their all-time min and max values and the respective dates
    stocks_min_max = pd.DataFrame(values, index=stocks.keys(), columns=['min_date', 'min', 'min_volume', 'max_date',
                                                                        'max', 'max_volume', 'profit'])
    # calculate date_range
    min_date = np.min([value.index.min() for value in stocks.values()])
    max_date = np.max([value.index.max() for value in stocks.values()])
    date_range = pd.date_range(start=min_date, end=max_date, freq='D').date

    print(len(stocks), 'stocks loaded')
    return stocks, stocks_min_max, date_range


def write_sequence_file(file, sequence):
    """
    :param file: The file name
    :param sequence: The sequence of transactions
    """
    with open(file, "w") as f:
        f.write(str(len(sequence)) + '\n')
        for transaction in sequence:
            f.write(' '.join(str(e) for e in transaction) + '\n')
