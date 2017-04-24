from flask import Flask
from flask_pymongo import PyMongo


# initialize flask app
app = Flask(__name__)
app.config.from_object(__name__)
# set-up database
app.config['MONGO_DBNAME'] = 'stocks'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/stocks'
mongo = PyMongo(app)




