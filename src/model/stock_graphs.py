import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from model.stock import calculate_yearly_return
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
#tls.set_credentials_file(username='lstrait10', api_key='x4GppVF3wg7KIJUd73jC')
#tls.set_credentials_file(username='lstrait2', api_key='uIQlfftMQF805rpyQS2D')
#tls.set_credentials_file(username='lstrait22', api_key='RDYgrEK0aJxCjsRSGz9U')
tls.set_credentials_file(username='lms17', api_key='PTOK52ARiRoiZ6Wr7UI8')

def plot_stock_price(stock_data):
	""" Create a plot of stock_price versus time

	:param stock_data: dictionary containing data for the stock
	:return:
	"""
	years = mdates.YearLocator()  # every year
	months = mdates.MonthLocator()  # every month
	yearsFmt = mdates.DateFormatter('%Y')

	prices = [entry['Close'] for entry in stock_data['historical_data']]
	# create date objects from date strings stored in dictionary
	dates = [datetime.datetime.strptime(entry['Date'], "%Y-%m-%d") for entry in stock_data['historical_data']]
	# sort by increasing date.
	prices.reverse()
	dates.reverse()
	# create plot.
	fig, ax = plt.subplots()
	plot = ax.plot(dates, prices)
	# label the plot.
	ax.set_ylabel("Share Price")
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


def plot_yearly_returns(stock_data):
	""" Create bar plot of yearly returns

	:param stock_data: stock to plot yearly returns for
	:return:
	"""
	years = np.array([year for year in range(2000, 2018)])
	yearly_returns = np.array([calculate_yearly_return(stock_data, str(year)) for year in years])
	# Create the plot
	fig = [go.Bar(
		x=years,
		y=yearly_returns,
		name="Yearly Returns: " + stock_data['name']
	)]
	plot_url = py.plot(fig, auto_open=False)
	# return plot_url to render to user
	return plot_url


def plot_returns_boxplot_stock(stock_data):
	""" Create box plot using yearly returns

	:param stock_data: stock data to create plot for
	:return:
	"""
	# calculate the yearly returns
	years = np.array([year for year in range(2000, 2018)])
	yearly_returns = np.array([calculate_yearly_return(stock_data, str(year)) for year in years])
	# create the plot
	fig, ax = plt.subplots()
	ax.boxplot(yearly_returns)
	ax.set_ylabel('Return %')
	# convert the plot to plotly
	plotly_fig = tls.mpl_to_plotly(fig)
	plot_url = py.plot(plotly_fig, auto_open=False)
	# return plot_url to render to user
	return plot_url