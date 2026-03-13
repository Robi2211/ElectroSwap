import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

db = None


def create_app(config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-electroswap')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/electroswap')

    if config:
        app.config.update(config)

    _init_db(app)
    _register_blueprints(app)

    return app


def _init_db(app):
    global db
    mongo_uri = app.config['MONGO_URI']
    client = MongoClient(mongo_uri)
    db_name = mongo_uri.rsplit('/', 1)[-1] or 'electroswap'
    db = client[db_name]
    app.extensions['mongo_db'] = db


def _register_blueprints(app):
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.main.routes import main_bp
    from app.blueprints.products.routes import products_bp
    from app.blueprints.cart.routes import cart_bp
    from app.blueprints.wishlist.routes import wishlist_bp
    from app.blueprints.orders.routes import orders_bp
    from app.blueprints.reviews.routes import reviews_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
