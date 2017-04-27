from model.portfolio import get_total_value_portfolio,  get_value_on_date
from model.stock import collect_stock_data,  calculate_yearly_return, calculate_largest_daily_loss, \
    calculate_historical_max, calculate_historical_min, calculate_largest_daily_gain, \
    calculate_yearly_return, regression_analysis
from model.clustering import format_stock_data, euclidean_dist, manhattan_dist, pearson_dist, assign_to_centroids, adjust_centroids, k_means, hierarchical_clustering
from model.prediction import get_accuracy, extract_feature_data, create_support_vector_regression, create_decision_tree_regression
import unittest


class ModelTests(unittest.TestCase):
    """ Unit tests to test helper methods related to stock and portfolio data

    """
    def setUp(self):
        # create fake JSON data
        self.test_stock = {"_id": "LL",
                      "name": "LL",
                      "symbol": "LL",
                      "dividend_per_share": "12.5",
                      "dividend_yield": "1.2",
                      "avg_daily_volume": "10",
                      "historical_data": [
                          {
                              "Adj_Close": "26.639999",
                              "Close": "26.639999",
                              "Date": "2016-03-29",
                              "High": "26.690001",
                              "Low": "26.49",
                              "Open": "26.51",
                              "Symbol": "VOD",
                              "Volume": "3251200"
                          },
                          {
                              "Adj_Close": "26.639999",
                              "Close": "27.639999",
                              "Date": "2016-03-28",
                              "High": "26.799999",
                              "Low": "26.620001",
                              "Open": "26.709999",
                              "Symbol": "VOD",
                              "Volume": "3731300"
                          }
                      ]}

        self.test_stock2 = {"_id": "L2",
                           "name": "L2",
                           "symbol": "L2",
                           "dividend_per_share": "0",
                           "dividend_yield": "0",
                           "avg_daily_volume": "0",
                           "historical_data": [
                               {
                                   "Adj_Close": "26.639999",
                                   "Close": "21.639999",
                                   "Date": "2016-03-29",
                                   "High": "26.690001",
                                   "Low": "26.49",
                                   "Open": "26.51",
                                   "Symbol": "VOD",
                                   "Volume": "3251200"
                               },
                               {
                                   "Adj_Close": "26.639999",
                                   "Close": "36.639999",
                                   "Date": "2016-03-28",
                                   "High": "26.799999",
                                   "Low": "26.620001",
                                   "Open": "26.709999",
                                   "Symbol": "VOD",
                                   "Volume": "3731300"
                               }
                           ]}
        self.test_portfolio = {
                      "Cash": 65000,
                      "_id": "test_port",
                      "name": "test_port",
                      "stocks": {
                        "LL": 208
                      }
                    }

    # test that yearly returns are correctly calculated
    def test_yearly_returns_valid(self):
        return_2016 = calculate_yearly_return(self.test_stock, '2016')
        # compare to yearly return calculated by hand
        self.assertEqual(return_2016, -3.617945138131155)

    # test yearly returns function handles year with no data
    def test_yearly_returns_invalid(self):
        return_2018 = calculate_yearly_return(self.test_stock, '2018')
        self.assertEqual(return_2018, 0)

    # test that historical max returns correct max
    def test_historical_max(self):
        hist_max = calculate_historical_max(self.test_stock)
        # date and price should be correct max.
        self.assertEqual(hist_max['max_price'], '27.639999')
        self.assertEqual(hist_max['date'], '2016-03-28')

    # test that historical min returns correct min
    def test_historical_min(self):
        hist_min = calculate_historical_min(self.test_stock)
        # date and price should be correct max.
        self.assertEqual(hist_min['min_price'], '26.639999')
        self.assertEqual(hist_min['date'], '2016-03-29')

    # test largest daily gain is correctly calculated
    def test_largest_daily_gain(self):
        daily_gain = calculate_largest_daily_gain(self.test_stock)
        # date and percentage change should be correct
        self.assertEquals(daily_gain['percentage_change'], 3.4818421370962978)
        self.assertEquals(daily_gain['date'], '2016-03-28')

    # test largest daily loss is correctly calculated
    def test_largest_daily_loss(self):
        daily_gain = calculate_largest_daily_loss(self.test_stock)
        # date and percentage change should be correct
        self.assertEquals(daily_gain['percentage_change'], 0.49037721614484336)
        self.assertEquals(daily_gain['date'], '2016-03-29')

    # test getting a regression for a stock
    def test_stock_regression(self):
        regression = regression_analysis(self.test_stock)
        # should be first order polynomial - value may change
        self.assertEqual(len(regression), 2)

    # test formatting stock data for clustering - single stock
    def test_format_cluster_data_single(self):
        formatted_data = format_stock_data([self.test_stock])
        # test that three lists properly created
        self.assertEqual(formatted_data['dividends'], [1.2])
        self.assertEqual(formatted_data['returns'], [-3.617945138131155])
        self.assertEqual(formatted_data['names'], ['LL'])

    # test formatting stock data for clustering - single stock
    def test_format_cluster_data_multiple(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # test that three lists properly created
        self.assertEqual(formatted_data['dividends'], [1.2, 0.0])
        self.assertEqual(formatted_data['returns'], [-3.617945138131155, -40.93886574614809])
        self.assertEqual(formatted_data['names'], ['LL', 'L2'])

    # test Euclidean distance to self
    def test_euclidean_self(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroid located at self
        centroid = (formatted_data['returns'][0], formatted_data['dividends'][0])
        # calculate distance
        euclidean_d = euclidean_dist(formatted_data['returns'][0], formatted_data['dividends'][0], centroid)
        # distance to self should be 0
        self.assertEqual(euclidean_d, 0)

    # test Euclidean distance to other
    def test_euclidean_other(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroid located at other
        centroid = (formatted_data['returns'][1], formatted_data['dividends'][1])
        # calculate distance
        euclidean_d = euclidean_dist(formatted_data['returns'][0], formatted_data['dividends'][0], centroid)
        # distance to self should be 0
        self.assertEqual(euclidean_d, 37.34020775290227)

    # test Manhattan distance to self
    def test_manhattan_self(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroid located at self
        centroid = (formatted_data['returns'][0], formatted_data['dividends'][0])
        # calculate distance
        manhattan_d = manhattan_dist(formatted_data['returns'][0], formatted_data['dividends'][0], centroid)
        # distance to self should be 0
        self.assertEqual(manhattan_d, 0)

    # test Manhattan distance to other
    def test_manhattan_other(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroid located at self
        centroid = (formatted_data['returns'][1], formatted_data['dividends'][1])
        # calculate distance
        manhattan_d = manhattan_dist(formatted_data['returns'][0], formatted_data['dividends'][0], centroid)
        # distance to self should be 0
        self.assertEqual(manhattan_d, 38.52092060801694)

    # test Manhattan distance to other
    def test_pearson_other(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroid located at self
        centroid = (formatted_data['returns'][1], formatted_data['dividends'][1])
        # calculate distance
        pearson_d = pearson_dist(formatted_data['returns'][0], formatted_data['dividends'][0], centroid)
        # distance to self should be non-zero
        self.assertEqual(pearson_d, 1)

    # test assigning stock to nearest centroid
    def test_assign_centroids(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroids with small offset
        centroid0 = (formatted_data['returns'][0] + 2.0, formatted_data['dividends'][0] + 1.0)
        centroid1 = (formatted_data['returns'][1] + 2.5, formatted_data['dividends'][1] + 1.2)
        # assign stocks to nearest centroid
        assigns = assign_to_centroids(formatted_data, [centroid0, centroid1], euclidean_dist)
        # check stocks assigned to centroid made near its location
        self.assertEqual(assigns[centroid0], [0])
        self.assertEqual(assigns[centroid1], [1])

    # test centroids correctly set to mean of members
    def test_reassign_centroids(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # create centroids with small offset
        centroid0 = (formatted_data['returns'][0] + 2.0, formatted_data['dividends'][0] + 1.0)
        centroid1 = (formatted_data['returns'][1] + 2.5, formatted_data['dividends'][1] + 1.2)
        # assign stocks to nearest centroid
        assigns = assign_to_centroids(formatted_data, [centroid0, centroid1], euclidean_dist)
        # re-calculate the centroid location
        new_centroids = adjust_centroids(formatted_data, [centroid0, centroid1], assigns)
        # since each centroid had one member should be at that (indiviudal stock) location now
        self.assertEqual(new_centroids[0], (-3.6179451381311551, 1.2))
        self.assertEqual(new_centroids[1], (-40.938865746148089, 0.0))

    # test a full run of k_means with k = 1 (should converage to mean of 2 stocks)
    def test_k_means_1(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # perform the clustering
        clusters = k_means(formatted_data, 1)
        # check results are expected - single cluster located in middle of 2 stocks
        self.assertEqual(clusters[0], (-22.278405442139622, 0.59999999999999998))

    # test a full run of k_means with k = 2 (should converge to location of 2 stocks)
    def test_k_means_2(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # perform the clustering
        clusters = k_means(formatted_data, 2)
        # check results are expected - one cluster on each stock
        # Note can make no assumptions about order!
        self.assertIn((-40.938865746148089, 0.0), clusters)
        self.assertIn((-3.6179451381311551, 1.2), clusters)

    # test hierarchical clustering
    def test_hierarchical_cluster(self):
        formatted_data = format_stock_data([self.test_stock, self.test_stock2])
        # perform the clustering
        clusters = hierarchical_clustering(formatted_data)
        # should be a single cluster (combine two stocks)
        self.assertEqual(clusters[0][0], 0.0)
        self.assertEqual(clusters[0][1], 1.0)
        # Euclidean distance should be distance between two members of top-level cluster
        self.assertEqual(clusters[0][2], 37.34020775290227)

    # test getting accuracy - zero percent
    def test_get_accuracy_zero(self):
        # create mock data
        feature_data = [1.0, 2.0, 3.0]
        predictions = [1.0, 2.0, 3.0]
        target_data = [40.0, 50.0, 60.0]
        # calculate the accuracy
        acc = get_accuracy(feature_data, target_data, predictions)
        # accuracy should be zero
        self.assertEqual(acc, 0.0)

    # test getting accuracy - zero percent
    def test_get_accuracy_nonzero(self):
        # create mock data
        feature_data = [1.0, 2.0, 3.0]
        # make predictions with 3.5 percent (allowable error) except for one
        predictions = [1.0, 2.0, 3.0]
        target_data = [1.5, 2.5, 33.5]
        # calculate the accuracy
        acc = get_accuracy(feature_data, target_data, predictions)
        # accuracy should be one hundred
        self.assertEqual(acc, 66.66666666666666)

    # test formatting data for use in ML algorithms - single entry
    def test_extra_feature_data_single(self):
        # extract the features and labels
        features, labels = extract_feature_data([self.test_stock2])
        # check that features and labels correctly created
        self.assertEqual(len(features), 1)
        self.assertIn([0.0], features)
        self.assertEqual(len(labels), 1)
        self.assertIn(-40.938865746148089, list(labels))

    # test formatting data for use in ML algorithms - multiple entries
    def test_extra_feature_data_multiple(self):
        # extract the features and labels
        features, labels = extract_feature_data([self.test_stock, self.test_stock2])
        # check that features and labels correctly created
        self.assertEqual(len(features), 2)
        self.assertIn([0.0], features)
        self.assertIn([1.2], features)
        self.assertEqual(len(labels), 2)
        self.assertIn(-40.938865746148089, list(labels))
        self.assertIn(-3.6179451381311551, list(labels))

    # make sure format of output is consistent and expected
    def test_dtree_regression(self):
        # extract features and labels
        features, labels = extract_feature_data([self.test_stock, self.test_stock2])
        # create decision tree classifier
        dtree = create_decision_tree_regression(features, labels)
        # check manually set parameters of decision tree correct
        self.assertEqual(dtree.max_depth, 2)
        self.assertEqual(dtree.min_samples_leaf, 1)

    # make sure format of output is consistent and expected
    def test_svm_regression(self):
        # extract features and labels
        features, labels = extract_feature_data([self.test_stock, self.test_stock2])
        # create decision tree classifier
        svm = create_support_vector_regression(features, labels)
        # check manually set parameters of svm correct
        self.assertEqual(svm.kernel, 'linear')
        self.assertEqual(svm.C, 100)


# make tests runnable
if __name__ == '__main__':
	unittest.main()