from app import app, mongo
from view.portfolio_views import construct_portfolio_blueprint
from view.stock_views import construct_stock_blueprint
from view.web_views import construct_web_blueprint

# configure views
app.register_blueprint(construct_stock_blueprint())
app.register_blueprint(construct_portfolio_blueprint())
app.register_blueprint(construct_web_blueprint())

if __name__ == '__main__':
    # run the app
    app.run()
