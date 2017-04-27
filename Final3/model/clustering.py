from random import random
import numpy as np
import math
from model.stock import calculate_yearly_return
from scipy.cluster.hierarchy import linkage
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
import plotly.figure_factory
#tls.set_credentials_file(username='lstrait10', api_key='x4GppVF3wg7KIJUd73jC')
#tls.set_credentials_file(username='lstrait2', api_key='uIQlfftMQF805rpyQS2D')
#tls.set_credentials_file(username='lstrait22', api_key='RDYgrEK0aJxCjsRSGz9U')
tls.set_credentials_file(username='lms17', api_key='PTOK52ARiRoiZ6Wr7UI8')

def format_stock_data(stock_data):
    """ Function to format stock data to facilitate clustering

    :param stock_data: list of JSON representations of stock data
    :return: dictionary of cluster data
    """
    cluster_data = dict()
    # cluster will be done using alpha and beta as features, names are used for labels in plotly
    cluster_data['returns'] = []
    cluster_data['dividends'] = []
    cluster_data['names'] = []
    # format data for each stock in provided data
    for stock in stock_data:
        if stock['dividend_yield'] is None:
            stock['dividend_yield'] = '0.0'
        cluster_data['dividends'].append(float(stock['dividend_yield']))
        cluster_data['returns'].append(calculate_yearly_return(stock, '2016'))
        cluster_data['names'].append(stock['symbol'])
    return cluster_data


def euclidean_dist(stock_returns, stock_dividends, centroid):
    """ Function to get euclidean distance from stock to a centroid

    :param stock_returns: 2016 returns for a stock
    :param stock_dividends: dividend yield for stock
    :param centroid: kmeans centroid to get distance to
    :return: euclidean distance
    """
    return math.sqrt(((stock_returns - centroid[0]) ** 2) + ((stock_dividends - centroid[1]) ** 2))


def manhattan_dist(stock_returns, stock_dividends, centroid):
    """ Function to calculate manhattan distance from stock to a centroid

    :param stock_returns: 2016 returns for a stock
    :param stock_dividends: dividend yield for stock
    :param centroid: kmeans centroid to get distance to
    :return: manhattan distance
    """
    return math.fabs(stock_returns - centroid[0] + stock_dividends - centroid[1])


def pearson_dist(stock_returns, stock_dividends, centroid):
    """ Function to calculate inverse pearson correlation between a stock and a centroid
    https://en.wikipedia.org/wiki/Pearson_correlation_coefficient

    :param stock_returns: 2016 returns for a stock
    :param stock_dividends: dividend yield for stock
    :param centroid: kmeans centroid to get distance to
    :return: manhattan distance
    """
    # calculate sum of squares
    sumsq1 = ((stock_returns ** 2) + (stock_dividends ** 2))
    sumsq2 = (centroid[0] ** 2) + (centroid[1] ** 2)
    # calculate correlation coeff.
    pearson_coeff = ((stock_returns * centroid[0]) + (stock_returns * centroid[1]) - ((stock_returns + stock_dividends) * sum(centroid) / 2))
    # normalize correlation coeff.
    normalizer = ((sumsq1 - ((stock_returns + stock_dividends) ** 2)) / 2) * ((sumsq2 - (sum(centroid)**2))/2)
    # check for undefined situations
    if normalizer == 0 or math.isnan(normalizer):
        return 1
    else:
        pearson_coeff /= normalizer
        # distance is inverse of correlation
        return 1.0 - pearson_coeff


def k_means(cluster_data, k, distance=manhattan_dist):
    """ Function to perform k-means clustering on given data

    :param cluster_data: cluster data for stocks (returns, dividends, name)
    :param k: number of clusters we're interested in
    :param distance: distance metric to use for similarity
    :return: the clusters the algorithm converges to
    """
    # calculate initial centroids randomly
    centroids = []
    for i in range(k):
        # each centroid should lie between min and max of each parameter
        random_return = random() * (max(cluster_data['returns']) - min(cluster_data['returns'])) + min(cluster_data['returns'])
        random_dividend = random() * (max(cluster_data['dividends']) - min(cluster_data['dividends'])) + min(cluster_data['dividends'])
        centroids.append((random_return, random_dividend))
    # alternate assigning stocks to centroids and updating centroids with mean
    for i in range(1000):
        centroid_members = assign_to_centroids(cluster_data, centroids, distance)
        centroids = adjust_centroids(cluster_data, centroids, centroid_members)
    return centroids


def hierarchical_clustering(cluster_data, algorithm='ward', distance='euclidean'):
    """ Function to perform hierarchical clustering for given data

    :param cluster_data: cluster data for stocks (returns, dividends, name)
    :param algorithm: algorithm to use for the clustering
    :param distance: distance metric to use for similarity
    :return: the clusters the algorithm converges to
    """
    # format the data for clustering analysis
    data = np.vstack((np.array(cluster_data['returns']), np.array(cluster_data['dividends']))).T
    # perform the clustering
    clustering = linkage(data, algorithm, metric=distance)
    clustering = clustering.tolist()
    # return the clustering
    return clustering


def assign_to_centroids(cluster_data, centroids, distance):
    """ Assign stocks to nearest centroid

    :param cluster_data: stock data in dictionary
    :param centroids: list of current centroids
    :param distance: distance function to use
    :return: mapping from centroids to data points
    """
    centroid_members = {}
    for centroid in centroids:
        centroid_members[centroid] = []
    # loop over all stocks
    for j in range(len(cluster_data['returns'])):
        closest_centroid = None
        closest_dist = float("inf")
        # find closest centroid to this stock
        for centroid in centroids:
            # calculate distance using provided distance function
            dist = distance(cluster_data['returns'][j], cluster_data['dividends'][j], centroid)
            # update closest distance if current distance closer
            if dist < closest_dist:
                closest_centroid = centroid
                closest_dist = dist
        # assign this stock to its closest centroid
        centroid_members[closest_centroid].append(j)
    return centroid_members


def get_cluster_assignments(cluster_data, centroids):
    """ Create list of clusters

    :param cluster_data: formatted stock data
    :param centroids: cluster centroids
    :return: list of list containing clusters
    """
    clusters = []
    centroid_members = assign_to_centroids(cluster_data, centroids, euclidean_dist)
    # loop over each cluster
    for centroid in centroid_members.keys():
        cluster = []
        # map idx to name of stock
        for idx in centroid_members[centroid]:
            cluster.append(cluster_data['names'][idx])
        # add cluster to lists of clusters
        clusters.append(cluster)
    return clusters


def adjust_centroids(cluster_data, centroids, centroid_members):
    """ Helper method to adjust location of centroid to mean of its members

    :param cluster_data: dictionary with stock data
    :param centroids: list of centroids for any iteration
    :param centroid_members: dictionary mapping centroid to its members
    :return: new centroids
    """
    new_centroids = []
    # loop over all centroids
    for centroid in centroids:
        returns = []
        dividends = []
        # loop over all stocks in this centroid
        for stock in centroid_members[centroid]:
            returns.append(cluster_data['returns'][stock])
            dividends.append(cluster_data['dividends'][stock])
        # set centroid location to mean of its members
        new_centroids.append((np.mean(returns), np.mean(dividends)))
    return new_centroids


def plot_clusters(cluster_data, centroids):
    """ Use Plotly to plot results of k-means clustering

    :param cluster_data: dictionary with stock data
    :param centroids: centroids of the k-means clustering
    :return: plotly URL
    """
    # plot the stock data
    data = [go.Scatter(
        x=cluster_data['returns'],
        y=cluster_data['dividends'],
        text=cluster_data['names'],
        mode='markers+text',
        name='stocks',
        marker=dict(size=14,
                    opacity=0.3,
                    )
    )]
    # add the centroids to the plot
    centroid_data = go.Scatter(
        x=[centroid[0] for centroid in centroids],
        y=[centroid[1] for centroid in centroids],
        mode='markers',
        name='centroids',
        marker=dict(size=18,
                    opacity=0.7,
                    color='rgb(255, 0, 0)'
                    )
    )
    data.append(centroid_data)
    # label the plot
    layout = go.Layout(
        xaxis=dict(
            title='Yearly Return',
        ),
        yaxis=dict(
            title='Dividend Yield',
        ),
        title='Stock performance clustering'
    )
    # create plot using plotly and return storage URL
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, auto_open=False)
    return plot_url


def plot_hierarchy(cluster_data):
    """ Plot a dendogram of the hierarchical clustering

    :param cluster_data: data to plot
    :return: a dendogram: y-axis is measure of similairty
    """
    # format the data for clustering analysis
    data = np.vstack((np.array(cluster_data['returns']), np.array(cluster_data['dividends']))).T
    # create the dendrogram after doing the clustering
    fig = tls.FigureFactory.create_dendrogram(data, labels=cluster_data['names'], linkagefun=lambda x: linkage(data, 'ward', metric='euclidean'))
    # create the plot
    plot_url = py.plot(fig, auto_open=False)
    # return URL of the plot.
    return plot_url
