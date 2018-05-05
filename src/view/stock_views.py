from flask import Blueprint, jsonify, abort
from model.stock import collect_stock_data,  calculate_yearly_return, calculate_largest_daily_loss, \
    calculate_historical_max, calculate_historical_min, calculate_largest_daily_gain, \
    calculate_yearly_return, regression_analysis
from model.stock_graphs import plot_stock_price, plot_yearly_returns, plot_returns_boxplot_stock
from model.clustering import k_means, format_stock_data, plot_clusters, plot_hierarchy, hierarchical_clustering
from model.prediction import extract_feature_data, create_decision_tree_regression, plot_decision_tree_regression, get_accuracy, create_support_vector_regression, plot_support_vector_regression
from app import mongo
import numpy as np


def construct_stock_blueprint():
    """ Blueprint to create routes for stock data
    :return: blueprint with registered routes
    """
    stock_blueprint = Blueprint('stock_blueprint', __name__)

    @stock_blueprint.route('/api/stocks', methods=['GET'])
    def get_stocks():
        """ API endpoint to retrieve info. for all stocks from db

        :return: JSON representation of stock data
        """
        stock_data = mongo.db.stocks.find()
        # check stock was found in db
        if stock_data is None:
            abort(404)
        return jsonify(list(stock_data)), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>', methods=['GET'])
    def get_stock(symbol):
        """ API endpoint to retrieve info. for stock from db

        :param symbol: symbol of stock to retrieve data for
        :return: JSON representation of stock data
        """
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        # check stock was found in db
        if stock_data is None:
            abort(404)
        return jsonify(stock_data), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>', methods=['POST'])
    def post_stock(symbol):
        """ API Endpoint to add or update info for stock

        :param symbol: symbol of stock to add or update data for
        :return: JSON representation of added or updated stock data
        """
        stock_data = collect_stock_data(symbol)
        # check stock was found from yahoo finance
        if stock_data is None:
            abort(404)
        # update or add stock to database
        mongo.db.stocks.update({"_id": stock_data["_id"]}, stock_data, upsert=True)
        return jsonify(stock_data), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/high', methods=['GET'])
    def get_max_price(symbol):
        """ API endpoint to get historical max price of stock

        :param symbol: stock to get max price for
        :return: JSON representation of max and data
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # find historical max
        max_entry = calculate_historical_max(stock_data)
        return jsonify(max_entry), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/low', methods=['GET'])
    def get_min_price(symbol):
        """ API endpoint to get historical min price of a stock

        :param symbol: stock to get min price for
        :return: JSON representation of min and data
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # find historical min
        min_entry = calculate_historical_min(stock_data)
        return jsonify(min_entry), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/largest_daily_gain', methods=['GET'])
    def get_largest_gain(symbol):
        """ API endpoint to get historical min price of a stock

        :param symbol: stock to get min price for
        :return: JSON representation of min and data
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # find largest daily gain
        entry = calculate_largest_daily_gain(stock_data)
        return jsonify(entry), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/largest_daily_loss', methods=['GET'])
    def get_largest_loss(symbol):
        """ API endpoint to get historical min price of a stock

        :param symbol: stock to get min price for
        :return: JSON representation of min and data
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # find largest daily loss
        entry = calculate_largest_daily_loss(stock_data)
        return jsonify(entry), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/yearly_returns', methods=['GET'])
    def get_yearly_returns(symbol):
        """ API endpoint to get yearly returns of a stock

        :param symbol: stock to get min price for
        :return: JSON representation of min and data
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # calculate yearly returns
        yearly_returns = {year: calculate_yearly_return(stock_data, year) for year in [str(i) for i in range(2000, 2018)]}
        return jsonify(yearly_returns), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/price_plot', methods=['GET'])
    def get_price_plot(symbol):
        """ API endpoint to get price vs. time plot for stock

        :param symbol: stock to get plot for
        :return:
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # generate the plot
        res = plot_stock_price(stock_data)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/yearly_returns_plot', methods=['GET'])
    def get_returns_plot(symbol):
        """ API endpoint to get yearly returns bar plot for stock

        :param symbol: stock to generate plot for
        :return:
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # generate the plot
        res = plot_yearly_returns(stock_data)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/returns_boxplot', methods=['GET'])
    def get_returns_boxplot(symbol):
        """ API endpoint to get boxplot of yearly returns

        :param symbol: stock to generate boxplot for
        :return:
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # generate the plot
        res = plot_returns_boxplot_stock(stock_data)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/<string:symbol>/regression', methods=['GET'])
    def get_regresison(symbol):
        """ API endpoint to get regression line for stock performance

        :param symbol: stock to do regression for
        :return: JSON representation regression line
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find_one({"_id": symbol})
        if stock_data is None:
            abort(404)
        # do the regression analysis
        coeffs = regression_analysis(stock_data)
        line = "y = (" + str(coeffs[0]) + ")x + " + str(coeffs[1])
        return jsonify({"regression_line": line}), 200

    @stock_blueprint.route('/api/stocks/kmeans_clustering/<int:k>', methods=['GET'])
    def kmeans_cluster_stocks(k):
        """ API endpoint to cluster stocks using k-means
        :param k: number of clusters
        :return: list of cluster centroids
        """
        stock_data = mongo.db.stocks.find()
        # check stock was found in db
        if stock_data is None:
            abort(404)
        clusters = k_means(format_stock_data(list(stock_data)), k)
        return jsonify({"centroids": clusters}), 200

    @stock_blueprint.route('/api/stocks/kmeans_clustering/<int:k>/plot', methods=['GET'])
    def kmeans_cluster_stocks_plot(k):
        """ API endpoint to cluster stocks using k-means
        :param k: number of clusters
        :return: list of cluster centroids
        """
        stock_data = mongo.db.stocks.find()
        # check stock was found in db
        if stock_data is None:
            abort(404)
        # format data and do clustering
        cluster_data = format_stock_data(list(stock_data))
        clusters = k_means(cluster_data, k)
        # make the plot
        res = plot_clusters(cluster_data, clusters)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/hierarchical_clustering', methods=['GET'])
    def hierarchy_cluster_stocks():
        """ API endpoint to cluster stocks using k-means
        :param k: number of clusters
        :return: list of cluster centroids
        """
        stock_data = mongo.db.stocks.find()
        # check stock was found in db
        if stock_data is None:
            abort(404)
        # format data and do clustering
        cluster_data = format_stock_data(list(stock_data))
        clusters = hierarchical_clustering(cluster_data)
        return jsonify({"clusters": clusters}), 200

    @stock_blueprint.route('/api/stocks/hierarchical_clustering/plot', methods=['GET'])
    def hierarchy_cluster_stocks_plot():
        """ API endpoint to cluster stocks using k-means
        :param k: number of clusters
        :return: list of cluster centroids
        """
        stock_data = mongo.db.stocks.find()
        # check stock was found in db
        if stock_data is None:
            abort(404)
        # format data and do clustering
        cluster_data = format_stock_data(list(stock_data))
        # make the plot
        res = plot_hierarchy(cluster_data)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/decision_tree', methods=['GET'])
    def get_decision_tree():
        """ API endpoint to get regression line for stock performance

        :param symbol: stock to do regression for
        :return: JSON representation regression line
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find()
        if stock_data is None:
            abort(404)
        # format the data
        features, targets = extract_feature_data(list(stock_data))
        # create the svm
        dtree = create_decision_tree_regression(features, targets)
        # make the plot
        get_accuracy(features, targets, dtree.predict(features))
        res = plot_decision_tree_regression(features, targets, dtree)
        return jsonify({"plot_url": res}), 200

    @stock_blueprint.route('/api/stocks/svm', methods=['GET'])
    def get_svm():
        """ API endpoint to get regression line for stock performance

        :param symbol: stock to do regression for
        :return: JSON representation regression line
        """
        # get stock data from db
        stock_data = mongo.db.stocks.find()
        if stock_data is None:
            abort(404)
        # format the data
        features, targets = extract_feature_data(list(stock_data))
        # create the svm
        svm = create_support_vector_regression(features, targets)
        # make the plot
        get_accuracy(features, targets, svm.predict(features))
        res = plot_support_vector_regression(features, targets, svm)
        return jsonify({"plot_url": res}), 200

    # return blueprint to main app
    return stock_blueprint