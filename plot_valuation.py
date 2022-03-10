import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

if __name__ == "__main__":
    # load small_valuation
    small_valuation = pd.read_csv('small_valuation.txt')
    small_valuation = small_valuation.rename({'Unnamed: 0': 'Date'}, axis=1)
    small_valuation['Date'] = pd.to_datetime(small_valuation['Date'])

    # load large_valuation
    large_valuation = pd.read_csv('large_valuation.txt')
    large_valuation = large_valuation.rename({'Unnamed: 0': 'Date'}, axis=1)
    large_valuation['Date'] = pd.to_datetime(large_valuation['Date'])

    # plot settings
    plt.rcParams["figure.figsize"] = (8, 5)
    pd.plotting.register_matplotlib_converters()
    sns.set_theme()

    # plot small valuation
    plt.figure()
    small_valuation = small_valuation[small_valuation['Date'] > pd.to_datetime(pd.datetime(2009, 1, 1))]
    plot1, = plt.plot(small_valuation['Date'], small_valuation['Portfolio'], c='orange')
    plot2, = plt.plot(small_valuation['Date'], small_valuation['Balance'], c='blue')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
    plt.title('Valuation\nSmall Sequence')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.legend([plot2, plot1], ['Balance', 'Portfolio'])
    plt.savefig('small_valuation.png')

    # plot large valuation
    plt.figure()
    large_valuation = large_valuation[large_valuation['Date'] > pd.to_datetime(pd.datetime(2009, 1, 1))]
    plot1, = plt.plot(large_valuation['Date'], large_valuation['Portfolio'], c='orange')
    plot2, = plt.plot(large_valuation['Date'], large_valuation['Balance'], c='blue')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
    plt.title('Valuation\nLarge Sequence')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.legend([plot2, plot1], ['Balance', 'Portfolio'])
    plt.savefig('large_valuation.png')
