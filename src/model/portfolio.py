import matplotlib.pyplot as plt
import numpy as np
from app import mongo
from model.stock import calculate_yearly_return


def get_total_value_portfolio(portfolio_data):
    """ Calculate total value of portfolio

    :param portfolio_data: JSON representation of portfolio_data
    :return: total value of portfolio
    """
    value = float(portfolio_data['Cash'])
    # get most recent price for each stock and add to value
    for stock in portfolio_data['stocks'].keys():
        stock_data = mongo.db.stocks.find_one({"_id": stock})
        if stock_data is not None:
            # multiply number of shares by share price and add to value
            value += (float(stock_data['historical_data'][0]['Close']) * float(portfolio_data['stocks'][stock]))

    return value


def get_value_on_date(portfolio_data, date):
    """ Calculate the value of the portfolio on date

    :param portfolio_data: JSON representation of portfolio_data
    :param date: date to calculate value of portfolio
    :return: value of portfolio on that date
    """
    value = float(portfolio_data['Cash'])
    for stock in portfolio_data['stocks'].keys():
        stock_data = mongo.db.stocks.find_one({"_id": stock})
        if stock_data is not None:
            # find value of share on date
            date_entry = filter(lambda x : x['Date'] == date, stock_data['historical_data'])
            # invalid date entered.
            if date_entry == []:
                return -1
            # multiply number of shares by share price and add to value
            value += (float(date_entry[0]['Close']) * float(portfolio_data['stocks'][stock]))
    return value


def get_excess_returns(portfolio_data, index_data):
    """ Helper method for alpha and beta.

    :param portfolio_data: JSON representation of portfolio data
    :param index_data: JSON representation of index data
    :return: excess returns for portfolio and index from years 2000 to 20018
    """
    years = [year for year in range(2000, 2018)]
    index_returns = [calculate_yearly_return(index_data, str(year)) for year in years]
    # calculate yearly returns for portfolio
    portfolio_returns = [0.0 for i in range(18)]
    for stock in portfolio_data['stocks'].keys():
        stock_data = mongo.db.stocks.find_one({"_id": stock})
        if stock_data is not None:
            stock_rets = []
            # get yearly return values for the stock
            for year in years:
                stock_rets.append(calculate_yearly_return(stock_data, str(year)))
                # add yearly return from stock to yearly return of overall portfolio
            portfolio_returns = [ret1 + ret2 for ret1, ret2 in zip(portfolio_returns, stock_rets)]

    return portfolio_returns, index_returns


def get_portfolio_alpha(portfolio_data, index_data):
    """ Calculate alpha of portfolio relative to S&P500 from start_date to present - alpha compares returns of portfolio
    to that of a "safe" benchmark like S&P500 or index fund.

    :param portfolio_data: JSON representation of portfolio_data
    :return: alpha of portfolio relative to S&P500
    """
    # calculate excess returns
    portfolio_returns, index_returns = get_excess_returns(portfolio_data, index_data)
    # calculate percentage return averages - "alpha"
    average_portfolio_return =  sum(portfolio_returns) / len(portfolio_returns)
    average_index_return = sum(index_returns) / len(index_returns)
    return average_portfolio_return - average_index_return


def get_portfolio_sharpe_ratio(portfolio_data, index_data):
    """ Calculate sharpe ratio of portfolio relative to S&P500 - sharpe ratio tells us returns of portfolio relative
    to that of a "safe" benchmark like S&P500, normalized by std (proxy for volatility) of portfolio

    :param portfolio_data: portfolio to calculate sharpe ratio for
    :param index_data: index to compare portfolio returns to
    :return: sharpe ratio of portfolio relative to index
    """
    # calculate excess returns
    portfolio_returns, index_returns = get_excess_returns(portfolio_data, index_data)
    # calculate yearly returns for index
    alpha = get_portfolio_alpha(portfolio_data, index_data)
    # caclculate standard deviation of portfolio return
    std_portfolio_return = np.std(portfolio_returns)
    # return sharpe ratio
    return alpha / std_portfolio_return


def get_portfolio_beta(portfolio_data, index_data):
    """ Calculate beta of portfolio relative to S&P500 - beta tells us volatility of portfolio relative to a "safe"
    benchmark like S&P500

    :param portfolio_data: JSON representation of portfolio data
    :param index_data: JSON representation of index data
    :return: beta value for portfolio relative to index
    """
    # calculate excess returns
    portfolio_returns, index_returns = get_excess_returns(portfolio_data, index_data)
    # calculate co-variance between returns of portfolio and benchmark
    covar = np.cov(np.vstack((portfolio_returns, index_returns)))[0][1]
    # calculate variance of portfolio returns
    var = np.var(portfolio_returns)
    # return beta value
    return covar/var


def get_portfolio_jensen_measure(portfolio_data, index_data):
    """ Calculate jensen measure of portfolio relative to S&P500 - jensen measure tells us returns of portfolio adjusted
    for market risk

        :param portfolio_data: JSON representation of portfolio data
        :param index_data: JSON representation of index data
        :return: jensen measure for portfolio relative to index
    """
    # calculate excess returns
    portfolio_returns, index_returns = get_excess_returns(portfolio_data, index_data)
    # calculate average return for portfolio and index
    average_portfolio_return = sum(portfolio_returns) / len(portfolio_returns)
    average_index_return = sum(index_returns) / len(index_returns)
    # calculate portfolio beta
    beta = get_portfolio_beta(portfolio_data, index_data)
    # calculate CAPM - use 2% as risk free rate
    capm = ((average_index_return/100) + (beta * ((average_index_return/100) - .02))) * 100
    # return the jensen measure
    return average_portfolio_return - capm