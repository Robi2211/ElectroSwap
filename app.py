"""
app.py – Flask application for the Electro Swap hardware shop.

Routes: Home, Product Detail, Add to Cart, View Cart, Checkout,
        My Orders, Admin Dashboard, Login, Register, Reviews.
"""

import os
from functools import wraps

from bson import ObjectId
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import database as db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32)
app.config["SESSION_TYPE"] = "filesystem"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator that redirects unauthenticated users to the login page."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Decorator that restricts access to admin users."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrapper


def _basket_count():
    """Return the number of items in the current user's basket."""
    if "user_id" not in session:
        return 0
    basket = db.get_basket(session["user_id"])
    if not basket or not basket.get("items"):
        return 0
    return sum(i["quantity"] for i in basket["items"])


@app.context_processor
def inject_globals():
    """Make basket count and categories available in every template."""
    return {
        "basket_count": _basket_count(),
        "categories": db.get_categories(),
    }


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = db.authenticate_user(email, password)
        if user:
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session["role"] = user.get("role", "customer")
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        street = request.form.get("street", "").strip()
        city = request.form.get("city", "").strip()
        zip_code = request.form.get("zip", "").strip()

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        uid = db.register_user(username, email, password, street, city, zip_code)
        if uid:
            session["user_id"] = str(uid)
            session["username"] = username
            session["role"] = "customer"
            flash("Account created successfully!", "success")
            return redirect(url_for("index"))
        flash("Username or email already taken.", "danger")
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Shop routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    products = db.get_products(search=search or None, category=category or None)
    return render_template(
        "index.html",
        products=products,
        search=search,
        active_category=category,
    )


@app.route("/product/<product_id>")
def product_detail(product_id):
    product = db.get_product(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("index"))
    reviews = db.get_reviews(product_id)
    can_review = False
    if "user_id" in session:
        can_review = db.has_purchased(session["user_id"], product_id)
    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews,
        can_review=can_review,
    )


# ---------------------------------------------------------------------------
# Basket routes
# ---------------------------------------------------------------------------

@app.route("/basket/add/<product_id>", methods=["POST"])
@login_required
def add_to_basket(product_id):
    quantity = int(request.form.get("quantity", 1))
    db.add_to_basket(session["user_id"], product_id, quantity)
    flash("Product added to basket.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/basket")
@login_required
def basket():
    items, total = db.get_basket_details(session["user_id"])
    return render_template("basket.html", items=items, total=total)


@app.route("/basket/remove/<product_id>", methods=["POST"])
@login_required
def remove_from_basket(product_id):
    db.remove_from_basket(session["user_id"], product_id)
    flash("Item removed from basket.", "info")
    return redirect(url_for("basket"))


@app.route("/basket/update/<product_id>", methods=["POST"])
@login_required
def update_basket(product_id):
    quantity = int(request.form.get("quantity", 1))
    db.update_basket_quantity(session["user_id"], product_id, quantity)
    return redirect(url_for("basket"))


# ---------------------------------------------------------------------------
# Checkout & Orders
# ---------------------------------------------------------------------------

@app.route("/checkout", methods=["POST"])
@login_required
def checkout_route():
    # Criterion 5.2: Transaction Logic
    success, result = db.checkout(session["user_id"])
    if success:
        flash("Order placed successfully!", "success")
        return redirect(url_for("orders"))
    flash(f"Checkout failed: {result}", "danger")
    return redirect(url_for("basket"))


@app.route("/orders")
@login_required
def orders():
    user_orders = db.get_orders(session["user_id"])
    return render_template("orders.html", orders=user_orders)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

@app.route("/review/<product_id>", methods=["POST"])
@login_required
def add_review(product_id):
    if not db.has_purchased(session["user_id"], product_id):
        flash("You can only review products you have purchased.", "warning")
        return redirect(url_for("product_detail", product_id=product_id))
    rating = request.form.get("rating", 5)
    comment = request.form.get("comment", "").strip()
    db.add_review(session["user_id"], product_id, rating, comment)
    flash("Review submitted!", "success")
    return redirect(url_for("product_detail", product_id=product_id))


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    # Criterion 2.8: Aggregation Pipeline
    analytics = db.get_analytics()
    order_stats = db.get_order_analytics()
    return render_template(
        "admin.html",
        analytics=analytics,
        order_stats=order_stats,
    )


# ---------------------------------------------------------------------------
# Seed route (convenience)
# ---------------------------------------------------------------------------

@app.route("/seed")
def seed():
    db.seed_db()
    flash("Database seeded with sample products!", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    db.create_indexes()
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true", port=5000)
