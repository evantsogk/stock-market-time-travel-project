import utils
import numpy as np
import pandas as pd
import time


class Account:
    """
    Class with all the functionality for stock exchanging.
    """
    def __init__(self, date_range, stocks, stocks_min_max, balance=1):
        self.balance = balance
        self.date_range = date_range
        self.stocks = stocks
        self.stocks_min_max = stocks_min_max

        self.history = pd.DataFrame(0, index=date_range, columns=['Balance', 'Portfolio'])
        self.history['Balance'][0] = balance
        self.sequence = []
        self.stocks_owned = {}

    def buy_low_sell_high(self, day, min_balance_fraction):
        """
        Buy or sell on different days. {buy-low, sell-high}
        """
        # buy
        made_low_high_transaction = False  # don't do intra-day exchange if have made low-high
        if day in self.stocks_min_max['min_date'].values:
            to_buy = self.stocks_min_max[self.stocks_min_max['min_date'] == day].index.values
            # best
            profits = [self.stocks_min_max['profit'].loc[[s]].values[0] for s in to_buy]
            max_profit = np.max(profits)
            if max_profit >= 10 or self.balance < 10:
                to_buy = to_buy[np.argmax(profits)]
                stock = self.stocks[to_buy].loc[[day]]
                possible_amount = np.floor(self.balance / (stock['Low'].values[0] + 0.01 * stock['Low'].values[0]))

                # don't exceed stock 10% volume of purchase date or selling date
                amount = np.min([possible_amount, np.floor(0.1 * stock['Volume'].values[0]),
                                 np.floor(0.1 * self.stocks_min_max['max_volume'].loc[to_buy])])

                if amount > 0:
                    price = amount * stock['Low'].values[0]
                    # leave at least balance * min_balance_fraction
                    if self.balance - (price + 0.01 * price) > self.balance * min_balance_fraction:
                        made_low_high_transaction = True
                        self.stocks_owned[to_buy] = amount
                        self.balance = self.balance - (price + 0.01 * price)
                        transaction = [str(day), 'buy-low', to_buy, amount]
                        self.sequence.append(transaction)
                        print(len(self.sequence), '. Transaction:', transaction, '\t|\t Balance:', self.balance)
        # sell
        if day in self.stocks_min_max['max_date'].values:
            all_to_sell = self.stocks_min_max[self.stocks_min_max['max_date'] == day].index.values
            for to_sell in all_to_sell:
                if to_sell in self.stocks_owned:
                    made_low_high_transaction = True
                    stock = self.stocks[to_sell].loc[[day]]
                    amount = self.stocks_owned[to_sell]  # already checked volume when bought
                    del self.stocks_owned[to_sell]
                    price = amount * stock['High'].values[0]
                    self.balance = self.balance + (price - 0.01 * price)
                    transaction = [str(day), 'sell-high', to_sell, amount]
                    self.sequence.append(transaction)
                    print(len(self.sequence), '. Transaction:', transaction, '\t|\t Balance:', self.balance)
        return made_low_high_transaction

    def buy_low_sell_close(self, day, made_low_high_transaction, min_intraday_profit):
        """
        Intra-day trade. Only consider {buy-low, sell-close} for simplicity.
        """
        if not made_low_high_transaction and self.balance > 100:
            temp_stocks = []
            profits = []
            amounts = []
            temp_to_exchange = []
            # find possible transactions
            for to_exchange, values in self.stocks.items():
                if day in values.index:
                    stock = values.loc[[day]]
                    low_close = stock['Close'].values[0] - stock['Low'].values[0]
                    if low_close >= min_intraday_profit:
                        possible_amount = np.floor(
                            self.balance / (stock['Low'].values[0] + 0.01 * stock['Low'].values[0]))
                        amount = np.min([possible_amount, np.floor(0.1 * stock['Volume'].values[0])])
                        if amount > 0:
                            temp_stocks.append(stock)
                            profits.append(low_close)
                            amounts.append(amount)
                            temp_to_exchange.append(to_exchange)
            # find best
            bought = []
            if profits:
                argsort = np.argsort(-np.multiply(profits, amounts))
                for i in argsort:
                    stock = temp_stocks[i]
                    amount = amounts[i]
                    to_exchange = temp_to_exchange[i]
                    # buy
                    price = amount * stock['Low'].values[0]
                    if self.balance - (price + 0.01 * price) >= 0:
                        self.balance = self.balance - (price + 0.01 * price)
                        transaction = [str(day), 'buy-low', to_exchange, amount]
                        self.sequence.append(transaction)
                        print(len(self.sequence), '. Transaction:', transaction, '\t|\t Balance:', self.balance)
                        bought.append(i)
                # sell
                for i in bought:
                    stock = temp_stocks[i]
                    amount = amounts[i]
                    to_exchange = temp_to_exchange[i]
                    # sell
                    price = amount * stock['Close'].values[0]
                    self.balance = self.balance + (price - 0.01 * price)
                    transaction = [str(day), 'sell-close', to_exchange, amount]
                    self.sequence.append(transaction)
                    print(len(self.sequence), '. Transaction:', transaction, '\t|\t Balance:', self.balance)

    def update_portfolio(self, day):
        """
        Value of stocks owned at any day.
        """
        portfolio = 0
        for stock, amount in self.stocks_owned.items():
            if day in self.stocks[stock].index:
                portfolio += amount * self.stocks[stock].loc[[day]]['Close'].values[0]
        self.history.loc[day, 'Portfolio'] = portfolio

    def make_money(self, min_intraday_profit, min_balance_fraction):
        """
        Main method. For each day, first {buy-low, sell-high} then {buy-low, sell-close}.
        """
        print('\nMaking money...')
        for day in date_range:
            # buy-low, sell-high
            made_low_high_transaction = self.buy_low_sell_high(day, min_balance_fraction)
            # buy-low, sell-close (intra-day)
            self.buy_low_sell_close(day, made_low_high_transaction, min_intraday_profit)

            self.history.loc[day, 'Balance'] = self.balance
            self.update_portfolio(day)
        print('\nAfter', len(self.sequence), 'transaction(s), your profit is', self.balance, 'dollars.')
        return self.sequence


if __name__ == "__main__":
    STOCKS_DIR = "Stocks/"

    sequence_type = input("Enter sequence type ('small' or 'large'): ")
    start = time.time()

    stocks, stocks_min_max, date_range = utils.read_data(STOCKS_DIR)
    account = Account(date_range, stocks, stocks_min_max)

    MIN_INTRADAY_PROFIT = 100  # min profit of an intra-day transaction
    MIN_BALANCE_FRACTION = 0  # leave at least balance * MIN_BALANCE_FRACTION after {buy-low} in inter-day exchange
    if sequence_type == 'large':
        MIN_INTRADAY_PROFIT = 1
        MIN_BALANCE_FRACTION = 0.1

    sequence = account.make_money(MIN_INTRADAY_PROFIT, MIN_BALANCE_FRACTION)
    utils.write_sequence_file(sequence_type+'.txt', sequence)
    account.history.to_csv(sequence_type+'_valuation.txt')

    end = time.time()
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Total time to run script: {:0>2}:{:0>2}:{:0>2}".format(int(hours), int(minutes), int(seconds)))
