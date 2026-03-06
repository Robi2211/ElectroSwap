"""ElectroSwap – Premium Hardware Shop application factory."""

import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

csrf = CSRFProtect()

# Global MongoDB references
mongo_client = None
db = None


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "electroswap-dev-secret-key-change-in-prod")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/electroswap")

    # --------------- CSRF Protection ---------------
    csrf.init_app(app)

    # --------------- MongoDB ---------------
    global mongo_client, db
    mongo_client = MongoClient(app.config["MONGO_URI"])
    db_name = app.config["MONGO_URI"].rsplit("/", 1)[-1].split("?")[0]
    db = mongo_client[db_name]
    app.db = db

    # Create indexes
    _ensure_indexes(db)

    # --------------- Flask-Login ---------------
    login_manager.init_app(app)

    from app.models import load_user  # noqa: E402
    login_manager.user_loader(load_user)

    # --------------- Blueprints ---------------
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.products.routes import products_bp
    from app.cart.routes import cart_bp
    from app.wishlist.routes import wishlist_bp
    from app.orders.routes import orders_bp
    from app.reviews.routes import reviews_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(wishlist_bp, url_prefix="/wishlist")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --------------- Context processors ---------------
    @app.context_processor
    def inject_cart_count():
        """Make cart item count available in all templates."""
        from flask_login import current_user
        count = 0
        if current_user.is_authenticated:
            basket = db.baskets.find_one({"user_id": current_user.get_id_object()})
            if basket and basket.get("items"):
                count = sum(item.get("quantity", 0) for item in basket["items"])
        return dict(cart_count=count)

    return app


def _ensure_indexes(database):
    """Create MongoDB indexes for performance (LB2 criterion 5.1)."""
    database.users.create_index("email", unique=True)
    database.products.create_index("category")
    database.products.create_index("brand")
    database.products.create_index("price")
    database.products.create_index([("name", "text"), ("description", "text"), ("brand", "text")])
    database.baskets.create_index("user_id", unique=True)
    database.wishlists.create_index("user_id")
    database.orders.create_index("user_id")
    database.reviews.create_index("product_id")
    database.reviews.create_index([("product_id", 1), ("user_id", 1)], unique=True)
