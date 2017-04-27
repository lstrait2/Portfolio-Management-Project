from app import mongo
from main import app
import json
import unittest


class APITests(unittest.TestCase):
    """ Unit tests to test API
    """

    def setUp(self):
        # set-up the test db
        app.config['TESTING'] = True
        self.flask_app = app.test_client()

    # get all portfolios from db
    def test_get_all_portfolios(self):
        # hit GET endpoint to get all portfolios
        res = self.flask_app.get('/api/portfolios')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # should be at least 2 portfolios in db to start
        self.assertGreaterEqual(len(data), 2)

    # get a specific portfolio from db
    def test_get_single_portfolio_valid(self):
        # hit GET endpoint to get test portfolio
        res = self.flask_app.get('/api/portfolios/test_portfolio')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(data['name'], 'test_portfolio')
        self.assertEqual(len(data['stocks']), 12)

    # attempt to get invalid portfolio from db
    def test_get_single_portfolio_invalid(self):
        # hit GET endpoint to get test portfolio
        res = self.flask_app.get('/api/portfolios/test_portfolio_invalid')
        # request should have returned 404
        self.assertEqual(res.status_code, 404)

    # attempt to post new portfolio to db
    def test_post_new_portfolio(self):
        # hit POST endpoint
        res = self.flask_app.post('/api/portfolios/new_test_portfolio', data=json.dumps({'name': 'new_test_portfolio', 'Cash': 1, 'stocks': {}}),
                                  headers={'Content-Type': 'application/json'})
        # request should have been succesful
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(data['name'], 'new_test_portfolio')
        self.assertEqual(data['Cash'], 1)

    # attempt to post an existing portfolio - old data should be overwritten
    def test_post_existing_portfolio(self):
        # hit POST endpoint
        res = self.flask_app.post('/api/portfolios/new_test_portfolio',
                                  data=json.dumps({'name': 'new_test_portfolio', 'Cash': 1, "stocks": {"JPM": 25, "GS": 10}}),
                                  headers={'Content-Type': 'application/json'})
        # request should have been succesful
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(data['name'], 'new_test_portfolio')
        self.assertEqual(data['Cash'], 1)
        # old data should be overwritten
        self.assertEqual(data['stocks']['JPM'], 25)

    # attempt to use put to update part of existing db
    def test_put_portfolio(self):
        # hit PUT endpoint
        res = self.flask_app.put('/api/portfolios/new_test_portfolio',
                                  data=json.dumps({"stocks": {"GS": 11}}),
                                  headers={'Content-Type': 'application/json'})
        # request should have been succesful
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # old data is not changed
        self.assertEqual(data['name'], 'new_test_portfolio')
        self.assertEqual(data['Cash'], 1)
        # stocks GS key updated
        self.assertEqual(data['stocks']['GS'], 11)

    # attempt to add new key using put
    def test_put_portfolio_new_stock(self):
        # hit PUT endpoint
        res = self.flask_app.put('/api/portfolios/new_test_portfolio',
                                 data=json.dumps({"stocks": {"MSFT": 34}}),
                                 headers={'Content-Type': 'application/json'})
        # request should have been succesful
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # old data is not changed
        self.assertEqual(data['name'], 'new_test_portfolio')
        self.assertEqual(data['Cash'], 1)
        # stocks GS key updated
        self.assertEqual(data['stocks']['MSFT'], 34)

    # attempt to delete a portfolio
    def test_delete_portfolio_valid(self):
        # hit DELETE endpoint
        res = self.flask_app.delete('/api/portfolios/new_test_portfolio')
        # request should have been successful
        self.assertEqual(res.status_code, 200)
        # check that the portfolio no longer exists
        res2 = self.flask_app.get('/api/portfolios/new_test_portfolio')
        self.assertEqual(res2.status_code, 404)

    # attempting to delete a portfolio that doesn't exist should 404
    def test_delete_portfolio_invalid(self):
        res = self.flask_app.delete('/api/portfolios/newww')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # attempt to get portfolio_value
    def test_get_portfolio_value_valid(self):
        res = self.flask_app.get('api/portfolios/test_portfolio/value')
        # request should have been succesful
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # check correct value structure returned - value itself may differ if db updated
        self.assertIn("value", data.keys())

    # attempt to get value with nonexistent portfolio
    def test_get_portfolio_invalid(self):
        res = self.flask_app.get('api/portfolios/new_test_portfolio/value')
        # request should have not been succesful
        self.assertEqual(res.status_code, 404)

    # get all stocks from db
    def test_get_all_stocks(self):
        # hit GET endpoint to get all portfolios
        res = self.flask_app.get('/api/stocks')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # should be at least 19 stocks at time
        self.assertGreater(len(data), 18)

    # get a specific stock from db
    def test_get_single_stock_valid(self):
        # hit GET endpoint to get test portfolio
        res = self.flask_app.get('/api/stocks/VOD')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertIn('Vodafone Group Plc', data['name'])
        self.assertEqual(data['symbol'], 'VOD')

    # attempt to get invalid portfolio from db
    def test_get_single_stock_invalid(self):
        # hit GET endpoint to get test portfolio
        res = self.flask_app.get('/api/stocks/NOT')
        # request should have returned 404
        self.assertEqual(res.status_code, 404)

    # attempt to post new stock
    def test_post_stock_new(self):
        res = self.flask_app.post('/api/stocks/IBM')
        # request should have worked - retrieved from YAHOO Finance API
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(data['name'], 'International Business Machines')
        self.assertEqual(data['symbol'], 'IBM')

    # attempt to post to update existing stock
    def test_post_stock_old(self):
        res = self.flask_app.post('/api/stocks/VOD')
        # request should have worked - retrieved from YAHOO Finance API
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertIn('Vodafone Group Plc', data['name'])
        self.assertEqual(data['symbol'], 'VOD')

    # get max price for stock
    def test_get_max_price(self):
        res = self.flask_app.get('/api/stocks/VOD/high')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertGreaterEqual(data["max_price"], '63.062869')

    # get max price for stock that doesn't exist
    def test_get_max_price_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/high')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get min price for stock
    def test_get_min_price(self):
        res = self.flask_app.get('/api/stocks/VOD/low')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertLessEqual(data["min_price"], '12.760077')

    # get min price for stock that doesn't exist
    def test_get_min_price_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/low')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get max daily gain for stock
    def test_get_max_daily_gain(self):
        res = self.flask_app.get('/api/stocks/VOD/largest_daily_gain')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertGreaterEqual(data["percentage_change"], 15.83008875853189)

    # get max daily gain for stock that doesn't exist
    def test_get_max_daily_gain_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/largest_daily_gain')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get max daily loss for stock
    def test_get_max_daily_loss(self):
        res = self.flask_app.get('/api/stocks/VOD/largest_daily_loss')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(data["percentage_change"], -9.961873687410572)

    # get max daily gain for stock that doesn't exist
    def test_get_max_daily_loss_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/largest_daily_loss')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get yearly returns for a stock
    def test_get_yearly_returns(self):
        res = self.flask_app.get('/api/stocks/VOD/yearly_returns')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected
        self.assertEqual(len(data.keys()), 18)
        self.assertEqual(data['2016'], -24.106863128513922)
        self.assertEqual(data['2011'], 6.134013166678295)

    # get max daily gain for stock that doesn't exist
    def test_get_yearly_returns_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/yearly_returns')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # test regression analysis on stock that exists
    def test_get_stock_regression_valid(self):
        res = self.flask_app.get('/api/stocks/VOD/regression')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what is expected - lines all of form y = ..
        self.assertEqual(data['regression_line'][0], 'y')
        # single x should be in equation (first order polynomial)
        self.assertIn('x', data['regression_line'])

    # get regression for stock that doesn't exist
    def test_get_stock_regression_invalid(self):
        res = self.flask_app.get('/api/stocks/VODDD/regression')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get value of test portfolio on a given date
    def test_get_portfolio_value_date(self):
        res = self.flask_app.get('api/portfolios/roth_lance/value/2017-01-26')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # asser data is what expected
        self.assertEqual(data['value'], 26407.659518)

    # get value of test portfolio on a given date
    def test_get_portfolio_value_date_invalid(self):
        res = self.flask_app.get('api/portfolios/roth_lance/value/2019-03-28')
        # request should have failed
        self.assertEqual(res.status_code, 404)

    # get alpha for roth portfolio
    def test_get_portfolio_alpha_valid(self):
        res = self.flask_app.get('api/portfolios/roth_lance/alpha')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what expected - alpha changes depending on current value of securities, but should be reasonabl
        self.assertLessEqual(data['alpha'], 100)
        self.assertGreaterEqual(data['alpha'], -100)

    # attempt to get alpha for invalid portfolio
    def test_get_portfolio_alpha_invalid(self):
        res = self.flask_app.get('api/portfolios/roth_lancess/alpha')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get sharpe for roth portfolio
    def test_get_portfolio_sharpe_valid(self):
        res = self.flask_app.get('api/portfolios/roth_lance/sharpe_ratio')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what expected
        #self.assertAlmostEqual(data['sharpe_ratio'], 0.09156187643034581)

    # attempt to get sharpe for invalid portfolio
    def test_get_portfolio_sharpe_invalid(self):
        res = self.flask_app.get('api/portfolios/roth_lancess/sharpe_ratio')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get beta for roth portfolio
    def test_get_portfolio_beta_valid(self):
        res = self.flask_app.get('api/portfolios/roth_lance/beta')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what expected
        #self.assertAlmostEqual(data['beta'], 0.14111989540221026)

    # attempt to get beta for invalid portfolio
    def test_get_portfolio_beta_invalid(self):
        res = self.flask_app.get('api/portfolios/roth_lancess/beta')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # get beta for roth portfolio
    def test_get_portfolio_jensen_valid(self):
        res = self.flask_app.get('api/portfolios/roth_lance/jensen_measure')
        # request should have worked
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # assert data is what expected - beta changes depending on current value of securities, but should be reasonabl
        #self.assertAlmostEqual(data['jensen_measure'], 9.302138920949517)

    # attempt to get beta for invalid portfolio
    def test_get_portfolio_jensen_invalid(self):
        res = self.flask_app.get('api/portfolios/roth_lancess/jensen_measure')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # attempt to get kmeans cluster for invalid portfolio
    def test_get_kmeans_valid(self):
        res = self.flask_app.get('api/stocks/kmeans_clustering/5')
        # request should have succeded
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # should be 5 centroids - cannot test content since nondeterministic
        self.assertEqual(len(data['centroids']), 5)

    # attempt to get kmeans cluster for invalid portfolio
    def test_get_kmeans_invalid(self):
        res = self.flask_app.get('api/stocks/roth_lancess/kmeans_clustering/5')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # attempt to get kmeans cluster for invalid
    def test_get_kmeans_plot_invalid(self):
        res = self.flask_app.get('api/stocks/roth_lancess/kmeans_clustering/5/plot')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # attempt to get kmeans cluster for valid
    def test_get_kmeans_plot_valid(self):
        res = self.flask_app.get('api/stocks/kmeans_clustering/5/plot')
        # request should have succeded
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # url in response
        self.assertIn('plot_url', data.keys())

    # attempt to get hierarchical cluster for invalid
    def test_get_hierarchical_invalid(self):
        res = self.flask_app.get('api/stocks/roth_lancess/hierarchical_clustering')
        # request should have 404ed
        self.assertEqual(res.status_code, 404)

    # attempt to get hierarchical cluster for valid
    def test_get_hierarchical_valid(self):
        res = self.flask_app.get('api/stocks/hierarchical_clustering')
        # request should have 404ed
        self.assertEqual(res.status_code, 200)
        # get output data
        data = json.loads(res.data)
        # should be 19 clusters - cannot test content since nondeterministic
        self.assertEqual(len(data['clusters']), 19)


#make tests runnable
if __name__ == '__main__':
	unittest.main()