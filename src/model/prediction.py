import numpy as np
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from model.stock import calculate_yearly_return, calculate_yearly_volume
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
#tls.set_credentials_file(username='lstrait10', api_key='x4GppVF3wg7KIJUd73jC')
#tls.set_credentials_file(username='lstrait2', api_key='uIQlfftMQF805rpyQS2D')
#tls.set_credentials_file(username='lstrait22', api_key='RDYgrEK0aJxCjsRSGz9U')
tls.set_credentials_file(username='lms17', api_key='PTOK52ARiRoiZ6Wr7UI8')

def extract_feature_data(stock_data):
    """ Helper function to extract feature data from stock_data for ML

    :param stock_data: raw stock data (JSON format)
    :return 2D array containing feature data
    """
    # Feature will be change in volume over year and dividend yield
    features = []
    labels = []
    # clean mixing data
    for stock in stock_data:
        # change null yield to 0
        if stock['dividend_yield'] is None:
            stock['dividend_yield'] = 0
    # collect data from each day in hisorical data for stock
    stock_data = sorted(stock_data, key = lambda x : x['dividend_yield'])
    for stock in stock_data:
        # if stock has no volume for this year, don't consider
        if stock['avg_daily_volume'] is None:
            continue
        labels.append(calculate_yearly_return(stock, '2016'))
        # append both features to list (feature matrix must be 2D)
        features.append([float(stock['dividend_yield'])])
        # return vectors in numpy arrays
    return np.array(features), np.array(labels)


def create_support_vector_regression(feature_data, target_data):
    """ Create support vector machine to predict price based on dividend

    :param feature_data: features to buiid svm on for all samples
    :param target_data: labels to build svm on for all samples
    :return: fitted svm model
    """
    # use linear kernel with fairly low C
    svm = SVR(kernel='linear', C=100)
    # fit the model using provided training data
    svm.fit(feature_data, target_data)
    # return the model
    return svm


def plot_support_vector_regression(feature_data, target_data, svm):
    """ Plot the fitted svm using plotly

    :param data: test data
    :param svm: model to plot
    :return: plotly URL
    """
    # get predictions from dtree
    predictions = svm.predict(feature_data)
    # plot the data points
    data = [go.Scatter(
        x=feature_data,
        y=target_data,
        mode='markers',
        name='data',
        marker=dict(size=14,
                    opacity=0.3,
                    )
    )]
    # plot the model predictions
    model = go.Scatter(
        x=feature_data,
        y=predictions,
        mode='lines+markers',
        name='svm',
        marker=dict(size=14,
                    opacity=0.3,
                    )
    )
    data.append(model)
    # create the plots
    layout = go.Layout(
        xaxis=dict(
            title='Dividend Yield',
        ),
        yaxis=dict(
            title='Yearly Return',
        ),
        title='Support Vector Machine Regression'
    )
    # create plot using plotly and return storage URL
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, auto_open=False)
    # return the plotly url
    return plot_url


def create_decision_tree_regression(feature_data, target_data):
    """ Create decision tree to attempt to predict price based on dividend

    :param feature_data: features to buiid tree on for all samples
    :param target_data: labels to build tree on for all samples
    :return: fitted decision tree model
    """
    # since only have ~300 samples, should prune tree as early as possible
    dtree = DecisionTreeRegressor(max_depth=2, random_state=None, min_samples_leaf=1)
    # fit the model to the formatted data
    dtree.fit(feature_data, target_data)
    # return the fitted model
    return dtree


def plot_decision_tree_regression(feature_data, target_data, dtree):
    """ Plot the created decision tree

    :param data: data to use for ploting
    :param dtree:model to use for plotting
    :return: Plotly URL
    """
    # get predictions from dtree
    predictions = dtree.predict(feature_data)
    # plot the data points
    data = [go.Scatter(
        x=feature_data,
        y=target_data,
        mode='markers',
        name='data',
        marker=dict(size=14,
                    opacity=0.3,
                    )
    )]
    # plot the model predictions
    model = go.Scatter(
        x=feature_data,
        y=predictions,
        mode='markers',
        name='Decision Tree predictions',
        marker=dict(size=14,
                    opacity=0.3,
                    )
    )
    data.append(model)
    # create the plots
    layout = go.Layout(
        xaxis=dict(
            title='Dividend Yield',
        ),
        yaxis=dict(
            title='Yearly Return',
        ),
        title='Decision Tree Regression'
    )
    # create plot using plotly and return storage URL
    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, auto_open=False)
    # return the plotly URL
    return plot_url


def get_accuracy(feature_data, target_data, predictions):
    """ Compute accuracy of model on given model

    :param feature_data: 2D feature-matrix
    :param target_data: 1D label vector
    :param model: scikit learn regression model
    :return: percentage accuracy of model
    """
    # get predictions from model
    total = 0
    correct = 0
    # loop over each example and compare actual to predicted label
    for i in range(0, len(predictions)):
        # allow a 3.5% margin-of-error
        if abs(predictions[i] - target_data[i]) < 3.5:
            correct += 1
        total += 1
    # return percentage of "correct" predictions
    return (float(correct) / total) * 100