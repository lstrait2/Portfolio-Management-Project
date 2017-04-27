from flask import Blueprint, request, jsonify, abort
from app import mongo
from model.portfolio import get_total_value_portfolio, get_value_on_date, get_portfolio_alpha, get_portfolio_sharpe_ratio, get_portfolio_beta, get_portfolio_jensen_measure
from model.portfolio_graphs import plot_portfolio_breakdown, plot_portfolio_value_vs_time, plot_portfolio_returns_vs_market, plot_returns_boxplot


def construct_portfolio_blueprint():
    """ Blueprint to create routes stock portfolio routes
    :return: blueprint with registered routes
    """
    portfolio_blueprint = Blueprint('portfolio_blueprint', __name__)

    @portfolio_blueprint.route('/api/portfolios', methods=['GET'])
    def get_portfolios():
        """ API Endpoint to get a portfolio
        :return: JSON representation of portfolio, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find()
        # check that a result was returned from db
        if portfolio_data is None:
            abort(404)
        return jsonify(list(portfolio_data)), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>', methods=['GET'])
    def get_portfolio(portfolio_name):
        """ API Endpoint to get a portfolio
        :return: JSON representation of portfolio, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # check that a result was returned from db
        if portfolio_data is None:
            abort(404)
        return jsonify(portfolio_data), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>', methods=['POST'])
    def post_portfolio(portfolio_name):
        """ API Endpoint to create a portfolio
        :return: JSON representation of new portfolio
        """
        portfolio_data = request.json
        # add name of portfolio to JSON and make it the primary key
        portfolio_data['name'] = portfolio_name
        portfolio_data['_id'] = portfolio_name
        # insert or update the portfolio data
        mongo.db.portfolios.update({"_id": portfolio_name}, portfolio_data, upsert=True)
        return jsonify(portfolio_data), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>', methods=['PUT'])
    def put_portfolio(portfolio_name):
        """ API Endpoint to update a portfolio
        :return: JSON representation of updated portfolio
        """
        portfolio = mongo.db.portfolios.find_one({"_id": portfolio_name})
        updated_portfolio = request.json
        # check that portfolio is in db and updated data was provided as JSON
        if portfolio is None or updated_portfolio is None:
            abort(404)
        # create update dict using dot notation to avoid over-writting other fields.
        update_dict = {}
        if "Cash" in updated_portfolio.keys():
            update_dict["Cash"] = updated_portfolio["Cash"]
        if "stocks" in updated_portfolio.keys():
            for stock in updated_portfolio["stocks"].keys():
                update_dict["stocks." + stock] = updated_portfolio["stocks"][stock]
        # use provided data to update data
        mongo.db.portfolios.update({"_id": portfolio_name}, {"$set": update_dict})
        # return updated data as JSON to user
        return jsonify(mongo.db.portfolios.find_one({"_id": portfolio_name})), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>', methods=['DELETE'])
    def delete_portfolio(portfolio_name):
        """ API endpoint to delete a portfolio

        :param porfolio_name: name of portfolio to delete
        :return: status of deletion
        """
        result = mongo.db.portfolios.delete_many({"_id": portfolio_name})
        # no such portfolio exists, 404
        if result.deleted_count == 0:
            abort(404)
        else:
            return jsonify({"status": "Successfully deleted " + portfolio_name})


    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/value', methods=['GET'])
    def get_portfolio_value(portfolio_name):
        """ API Endpoint to get a portfolio
        :return: JSON representation of portfolio, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # check portfolio data was found in db
        if portfolio_data is None:
            abort(404)
        # calculate value of portfolio
        value = get_total_value_portfolio(portfolio_data)
        return jsonify({'value': value}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/breakdown_plot', methods=['GET'])
    def get_breakdown_plot(portfolio_name):
        """ API endpoint to get breakdown percentages of portfolio

        :param portfolio_name: name of portfolio to generate plot for
        :return:
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # check portfolio data was found in db
        if portfolio_data is None:
            abort(404)
        # create plot and give it to user
        res = plot_portfolio_breakdown(portfolio_data)
        return jsonify({"plot_url": res}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/value/<string:date>', methods=['GET'])
    def get_portfolio_value_date(portfolio_name, date):
        """ API Endpoint to get a portfolio on given date
        :return: JSON representation of portfolio on given date, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # check portfolio data was found in db
        if portfolio_data is None:
            abort(404)
        # calculate value of portfolio on given date
        value = get_value_on_date(portfolio_data, date)
        # invalid date entered
        if value == -1:
            abort(404)
        return jsonify({'value': value, 'Date': date}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/alpha', methods=['GET'])
    def get_portfolio_alpha_endpoint(portfolio_name):
        """ API Endpoint to get a portfolio alpha
        :return: JSON representation of portfolio alpha, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio and index data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # calculate beta value of portfolio on given date
        value = get_portfolio_alpha(portfolio_data, index_data)
        return jsonify({'alpha': value}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/sharpe_ratio', methods=['GET'])
    def get_portfolio_sharpe_ratio_endpoint(portfolio_name):
        """ API Endpoint to get a portfolio's sharpe ratio
        :return: JSON representation of portfolio on sharpe, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio and index data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # calculate beta value of portfolio on given date
        value = get_portfolio_sharpe_ratio(portfolio_data, index_data)
        return jsonify({'sharpe_ratio': value}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/beta', methods=['GET'])
    def get_portfolio_beta_endpoint(portfolio_name):
        """ API Endpoint to get a portfolio beta
        :return: JSON representation of portfolio beta, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio and index data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # calculate beta value of portfolio on given date
        value = get_portfolio_beta(portfolio_data, index_data)
        return jsonify({'beta': value}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/jensen_measure', methods=['GET'])
    def get_portfolio_jensen_measure_endpoint(portfolio_name):
        """ API Endpoint to get a portfolio jensen measure
        :return: JSON representation of portfolio jensen measure, 404 if no such portfolio
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio and index data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # calculate jensen_measure value of portfolio on given date
        value = get_portfolio_jensen_measure(portfolio_data, index_data)
        return jsonify({'jensen_measure': value}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/value_plot', methods=['GET'])
    def get_value_plot(portfolio_name):
        """ API endpoint to get plot of value of portfolio over time

        :param portfolio_name: name of portfolio to generate plot for
        :return:
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # check portfolio data was found in db
        if portfolio_data is None:
            abort(404)
        # create plot and give it to user
        res = plot_portfolio_value_vs_time(portfolio_data)
        return jsonify({"plot_url": res}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/returns_plot', methods=['GET'])
    def get_returns_plot(portfolio_name):
        """ API endpoint to get portfolio returns vs. market

        :param portfolio_name: name of portfolio to generate plot for
        :return:
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # create plot and give it to user
        res = plot_portfolio_returns_vs_market(portfolio_data, index_data)
        return jsonify({"plot_url": res}), 200

    @portfolio_blueprint.route('/api/portfolios/<string:portfolio_name>/boxplot', methods=['GET'])
    def get_returns_boxplot(portfolio_name):
        """ API endpoint to get portfolio returns boxplot

        :param portfolio_name: name of portfolio to generate plot for
        :return:
        """
        portfolio_data = mongo.db.portfolios.find_one({"_id": portfolio_name})
        # ^GSPC is symbol for S&P500
        index_data = mongo.db.stocks.find_one({"_id": "^GSPC"})
        # check portfolio data was found in db
        if portfolio_data is None or index_data is None:
            abort(404)
        # create plot and give it to user
        res = plot_returns_boxplot(portfolio_data, index_data)
        return jsonify({"plot_url": res}), 200

    return portfolio_blueprint