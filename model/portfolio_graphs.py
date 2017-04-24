from app import mongo
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from model.portfolio import get_value_on_date, get_excess_returns
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
#tls.set_credentials_file(username='lstrait10', api_key='x4GppVF3wg7KIJUd73jC')
tls.set_credentials_file(username='lstrait2', api_key='uIQlfftMQF805rpyQS2D')


def plot_portfolio_breakdown(portfolio_data):
    """ Create pie chart with portfolio breakdown

    :param portfolio_data: portfolio to create plot for
    :return: plotly URL
    """
    labels = ['Cash']
    values = [float(portfolio_data['Cash'])]
    # get value of each stock in portfolio
    for stock in portfolio_data['stocks'].keys():
        stock_data = mongo.db.stocks.find_one({"_id": stock})
        # only consider stocks we have valid data for in breakdown
        if stock_data is not None:
            labels.append(stock)
            values.append(float(stock_data['historical_data'][0]['Close']) * float(portfolio_data['stocks'][stock]))
    # create the plot
    fig = {
        'data': [{'labels': labels,
                  'values': values,
                  'type': 'pie'}],
        'layout': {'title': 'Portfolio Breakdown'}
    }
    plot_url = py.plot(fig, auto_open=False)
    # return plot_url to render to user
    return plot_url


def plot_portfolio_value_vs_time(portfolio_data):
    """ Create a chart of portfolio value over time

    :param portfolio_data: portfolio to create plot for
    :return: plotly URL
    """
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%Y')
    dates = [str(year) + '-12-01' for year in range(2000, 2017)]
    prices = [get_value_on_date(portfolio_data, date) for date in dates]
    # create date objects from date strings stored in dictionary
    dates = [datetime.datetime.strptime(date, "%Y-%m-%d") for date in dates]
    # sort by increasing date.
    prices.reverse()
    dates.reverse()
    # create plot.
    fig, ax = plt.subplots()
    plot = ax.plot(dates, prices)
    # label the plot.
    ax.set_ylabel("Portfolio Value")
    ax.set_xlabel("Year")
    # format the date: code taken from matplotlib docs: http://matplotlib.org/examples/api/date_demo.html
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)
    datemin = datetime.date(2000, 1, 1)
    datemax = datetime.date(2018, 1, 1)
    ax.set_xlim(datemin, datemax)
    ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
    ax.grid(True)
    fig.autofmt_xdate()
    # convert the plot to plotly
    plotly_fig = tls.mpl_to_plotly(fig)
    plot_url = py.plot(plotly_fig, auto_open=False)
    # return plot_url to render to user
    return plot_url


def plot_portfolio_returns_vs_market(portfolio_data, index_data):
    """ Create plot of portfolio returns vs. market returns each year

    :param portfolio_data: portfolio to compare to market
    :param index_data: index representing market returns
    :return: plotly URL
    """
    # calculate yearly returns for portfolio and index
    years = np.array([year for year in range(2000, 2018)])
    portfolio_returns, index_returns = get_excess_returns(portfolio_data, index_data)
    # Create the plot
    portfolio_plot = go.Bar(
        x=years,
        y=portfolio_returns,
        name=portfolio_data['name']
    )
    index_plot = go.Bar(
        x=years,
        y=index_returns,
        name=index_data['name']
    )
    layout = go.Layout(
        barmode='group'
    )
    fig = go.Figure(data=[portfolio_plot, index_plot], layout=layout)
    plot_url = py.plot(fig, auto_open=False)
    # return plot_url to render to user
    return plot_url


def plot_returns_boxplot(portfolio_data, index_data):
    """ Create boxplot of portfolio returns

    :param portfolio_data: portfolio to make plot for
    :param index_data: index to make plot for
    :return: plotly URL
    """
    years = np.array([year for year in range(2000,2018)])
    yearly_returns, _ = get_excess_returns(portfolio_data, index_data)
    # create the plot
    fig, ax = plt.subplots()
    ax.boxplot(yearly_returns)
    ax.set_ylabel("Return %")
    # convert the plot to plotly
    plotly_fig = tls.mpl_to_plotly(fig)
    plot_url = py.plot(plotly_fig, auto_open=False)
    # return plot_url to render to user
    return plot_url

