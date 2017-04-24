import time
from yahoo_finance import Share
import numpy as np


def collect_stock_data(symbol):
	""" Collect stock data for stock with symbol symbol
	:param symbol: symbol of stock to collect data for
	:return: dictionary containing stock data
	"""
	stock_data = dict()
	stock = Share(symbol)
	# check if symbol was for a valid stock
	name = stock.get_name()
	if name == 'N/A':
		return None
	stock_data['symbol'] = symbol
	stock_data['name'] = name
	# get all data between today and start of 21st century
	start_date = time.strftime("2000-01-01")
	end_date = time.strftime("%Y-%m-%d")
	stock_data['historical_data']= stock.get_historical(start_date, end_date)
	# get dividend information
	stock_data['dividend_per_share'] = stock.get_dividend_share()
	stock_data['dividend_yield'] = stock.get_dividend_yield()
	# get volume information
	stock_data['avg_daily_volume'] = stock.get_avg_daily_volume()
	# primary key is the stock's symbol
	stock_data['_id'] = symbol
	return stock_data


def calculate_yearly_return(stock_data, year):
	""" Calculate yearly return for given stock

	:param stock_data: data for stock
	:param year: year to calculate returns for
	:return: yearly return for given stock
	"""
	entries_for_year = [entry for entry in stock_data['historical_data'] if entry['Date'][:4] == year]
	# if stock wasn't traded in that year, no return
	if len(entries_for_year) == 0:
		return 0
	end_price = float(entries_for_year[0]['Close'])
	start_price = float(entries_for_year[-1]['Close'])
	return ((end_price - start_price) / start_price) * 100


def calculate_historical_max(stock_data):
	""" Calculate max. historical value of a stock

	:param stock_data: stock to calculate max. historical value for
	:return: max historical price and data it occurred on
	"""
	# find date with maximum price
	max_entry = max(stock_data['historical_data'], key=lambda x: x['Close'])
	# return max price and date of occurrence as dictionary
	return {"max_price": max_entry["Close"], "date": max_entry["Date"]}


def calculate_historical_min(stock_data):
	""" Calculate max. historical value of a stock

	:param stock_data: stock to calculate max. historical value for
	:return: max historical price and data it occurred on
	"""
	# find date with maximum price
	min_entry = min(stock_data['historical_data'], key=lambda x: x['Close'])
	# return max price and date of occurrence as dictionary
	return {"min_price": min_entry["Close"], "date": min_entry["Date"]}


def calculate_largest_daily_gain(stock_data):
	""" Calc. largest daily gain for stock

	:param stock_data: stock to calculate max daily gain for
	:return: maximum daily gain and day it occurred
	"""
	# find entry with max daily change
	max_entry = max(stock_data['historical_data'], key=lambda x: ((float(x['Close']) - float(x['Open'])) / float(x['Open'])))
	# calculate percentage change for this day
	percent_gain = (float(max_entry['Close']) - float(max_entry['Open'])) / float(max_entry['Open']) * 100
	return {"percentage_change": percent_gain, "date": max_entry["Date"]}


def calculate_largest_daily_loss(stock_data):
	""" Calc. largest daily loss for stock

	:param stock_data: stock to calculate max daily loss for
	:return: maximum daily loss and day it occurred
	"""
	# find entry with max daily change
	max_entry = min(stock_data['historical_data'], key=lambda x: ((float(x['Close']) - float(x['Open'])) / float(x['Open'])))
	# calculate percentage change for this day
	percent_gain = (float(max_entry['Close']) - float(max_entry['Open'])) / float(max_entry['Open']) * 100
	return {"percentage_change": percent_gain, "date": max_entry["Date"]}


def regression_analysis(stock_data):
	""" Compute a simple regression line for the stock's yearly returns since turn of century.

	:param stock_data: stock to do regression analysis with
	:return: regression line for stock
	"""
	# x-axis is year
	years = np.array([year for year in range(2000,2018)])
	# y-axis is percent return
	returns = np.array([calculate_yearly_return(stock_data, str(year)) for year in years])
	# compute a regression line with degree 1
	return np.polyfit(years, returns, 1)


