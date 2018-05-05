from flask import Blueprint, render_template, abort
from app import mongo
from model.portfolio import get_total_value_portfolio, get_portfolio_alpha, get_portfolio_sharpe_ratio, get_portfolio_beta, get_portfolio_jensen_measure
from model.portfolio_graphs import plot_portfolio_breakdown, plot_portfolio_value_vs_time, plot_portfolio_returns_vs_market, plot_returns_boxplot
from model.stock import  calculate_largest_daily_loss, \
    calculate_historical_max, calculate_historical_min, calculate_largest_daily_gain, regression_analysis
from model.stock_graphs import plot_stock_price, plot_yearly_returns, plot_returns_boxplot_stock
from model.clustering import plot_clusters, plot_hierarchy, format_stock_data, k_means, get_cluster_assignments
from model.prediction import plot_decision_tree_regression, plot_support_vector_regression, extract_feature_data, create_support_vector_regression, create_decision_tree_regression


def construct_web_blueprint():
    """ Blueprint to create routes for web views
    :return: blueprint with registered routes
    """
    web_blueprint = Blueprint('web_blueprint', __name__)

    @web_blueprint.route('/', methods=['GET'])
    def index():
        """ render template for index of site. Use Jinja to dynamically display assignment data

        :return: HTML rendering
        """
        # get all portfolios from portfolios table
        portfolios = list(mongo.db.portfolios.find({}))
        # tack on value fields
        for portfolio in portfolios:
            portfolio['value'] = get_total_value_portfolio(portfolio)
        return render_template('index.html', portfolios=portfolios)

    @web_blueprint.route('/portfolios/<string:portfolio_name>', methods=['GET'])
    def get_portfolio(portfolio_name):
        """ render template for portfolio page of site. USe Jinja to dynamically display assignment data

        :return: HTML rendering
        """
        # look up portfolio in mongo db
        portfolio = mongo.db.portfolios.find_one({"_id": portfolio_name})
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check that a result was returned from db
        if portfolio is None or index_data is None:
            abort(404)
        # tack on value field
        portfolio['value'] = get_total_value_portfolio(portfolio)
        # tack on the plotly urls
        portfolio['breakdown_plot'] = plot_portfolio_breakdown(portfolio)
        portfolio['value_plot'] = plot_portfolio_value_vs_time(portfolio)
        portfolio['returns_plot'] = plot_portfolio_returns_vs_market(portfolio, index_data)
        portfolio['boxplot'] = plot_returns_boxplot(portfolio, index_data)
        # tack on statistics
        portfolio['alpha'] = get_portfolio_alpha(portfolio, index_data)
        portfolio['beta'] = get_portfolio_beta(portfolio, index_data)
        portfolio['sharpe_ratio'] = get_portfolio_sharpe_ratio(portfolio, index_data)
        portfolio['jensen_measure'] = get_portfolio_jensen_measure(portfolio, index_data)
        # add stock data
        stock_data = list(mongo.db.stocks.find())
        # perform ML
        features, targets = extract_feature_data(stock_data)
        svm = create_support_vector_regression(features, targets)
        dtree = create_decision_tree_regression(features, targets)
        # add future return fields
        stocks = {}
        for stock in stock_data:
            features_stock, _ = extract_feature_data([stock])
            if len(features_stock) == 0:
                stocks[stock['symbol']] = 0.0
            else:
                stocks[stock['symbol']] = (svm.predict(features_stock)[0] + dtree.predict(features_stock)[0]) / 2
        return render_template('portfolio.html', portfolio=portfolio, stocks=stocks)

    @web_blueprint.route('/stocks/<string:stock_name>', methods=['GET'])
    def get_stock(stock_name):
        """ render template for stock page of site. USe Jinja to dynamically display assignment data

        :return: HTML rendering
        """
        # look up stock in mongo db
        stock = mongo.db.stocks.find_one({"_id": stock_name})
        # check that a result was returned from db
        if stock is None:
            abort(404)
        # tack on plotly urls
        stock['price_plot'] = plot_stock_price(stock)
        stock['boxplot'] = plot_returns_boxplot_stock(stock)
        stock['returns_plot'] = plot_yearly_returns(stock)
        # tack on statistics
        stock['max'] = calculate_historical_max(stock)
        stock['min'] = calculate_historical_min(stock)
        stock['best'] = calculate_largest_daily_gain(stock)
        stock['worst'] = calculate_largest_daily_loss(stock)
        # predict future price using ML
        stock_data = list(mongo.db.stocks.find())
        features, targets = extract_feature_data(stock_data)
        # create the svm and dtree
        svm = create_support_vector_regression(features, targets)
        dtree = create_decision_tree_regression(features, targets)
        # predict price of the stock
        features_stock, _ = extract_feature_data([stock])
        stock['future_returns'] = (svm.predict(features_stock)[0] + dtree.predict(features_stock)[0]) / 2
        # render the HTML
        return render_template('stock.html', stock=stock)

    @web_blueprint.route('/stocks', methods=['GET'])
    def get_stocks():
        """ render template for stock page of site. USe Jinja to dynamically display assignment data

        :return: HTML rendering
        """
        # look up stock in mongo db
        stock_data = list(mongo.db.stocks.find())
        # check that a result was returned from db
        if stock_data is None:
            abort(404)
        # perform ML algos
        features, targets = extract_feature_data(stock_data)
        # create the svm and dtree
        svm = create_support_vector_regression(features, targets)
        dtree = create_decision_tree_regression(features, targets)
        # tack on plotly urls
        formatted_data = format_stock_data(stock_data)
        clusters = k_means(formatted_data, 3)
        cluster_assignments = get_cluster_assignments(formatted_data, clusters)
        plots = {}
        plots['kmeans'] = plot_clusters(formatted_data, clusters)
        plots['hierarchy'] = plot_hierarchy(formatted_data)
        plots['svm'] = plot_support_vector_regression(features, targets, svm)
        plots['dtree'] = plot_decision_tree_regression(features, targets, dtree)
        # add expected returns
        stock_rets = {}
        for stock in stock_data:
            features_stock, _ = extract_feature_data([stock])
            if len(features_stock) == 0:
                stock_rets[stock['symbol']] = 0.0
            else:
                stock_rets[stock['symbol']] = (svm.predict(features_stock)[0] + dtree.predict(features_stock)[0]) / 2
        # render the HTML
        return render_template('stocks.html', stocks=stock_data, plots=plots, clusters=cluster_assignments, stock_rets=stock_rets)
    # return blueprint to main app
    return web_blueprint
