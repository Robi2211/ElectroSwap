"""
app.py – Flask Application for ElectroSwap Hardware Online Shop.

Provides routes for browsing products, viewing product details and reviews,
managing the shopping basket, and processing checkout.
Refers to Criteria 5.5–5.6 of the grading rubric.
"""

import uuid

from bson import ObjectId
from flask import Flask, redirect, render_template, request, session, url_for

import database as db

app = Flask(__name__)
app.secret_key = "electroswap-secret-key-change-in-production"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _session_id():
    """Return a persistent session id for the current browser session."""
    if "sid" not in session:
        session["sid"] = str(uuid.uuid4())
    return session["sid"]


def _basket_count():
    """Return the total number of items in the current basket."""
    basket = db.get_basket(_session_id())
    return sum(i["quantity"] for i in basket.get("items", []))


@app.context_processor
def inject_basket_count():
    """Make basket_count available in every template."""
    return {"basket_count": _basket_count()}


# ---------------------------------------------------------------------------
# Routes – Criteria 5.5 / 5.6
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Home page: show products with optional category filter and search."""
    category = request.args.get("category")
    search = request.args.get("search")
    products = db.get_all_products(category=category, search=search)
    categories = db.get_categories()
    stats = db.avg_price_per_category()  # Criterion 2.8
    return render_template(
        "index.html",
        products=products,
        categories=categories,
        selected_category=category,
        search=search or "",
        stats=stats,
    )


@app.route("/product/<product_id>")
def product_detail(product_id):
    """Product detail page: show specs and reviews."""
    product = db.get_product(product_id)
    if not product:
        return "Product not found", 404
    reviews = db.get_reviews_for_product(product_id)
    avg_rating = 0
    if reviews:
        avg_rating = round(
            sum(r["rating"] for r in reviews) / len(reviews), 1
        )
    return render_template(
        "product.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
    )


@app.route("/product/<product_id>/review", methods=["POST"])
def add_review(product_id):
    """Submit a review for a product."""
    author = request.form.get("author", "Anonymous")
    rating = request.form.get("rating", 5)
    comment = request.form.get("comment", "")
    db.add_review(product_id, author, rating, comment)
    return redirect(url_for("product_detail", product_id=product_id))


# ---------------------------------------------------------------------------
# Basket
# ---------------------------------------------------------------------------


@app.route("/basket")
def basket():
    """Show the current basket."""
    basket_doc = db.get_basket(_session_id())
    items = []
    total = 0.0
    for entry in basket_doc.get("items", []):
        product = db.get_product(entry["product_id"])
        if product:
            line_total = product["price"] * entry["quantity"]
            items.append({
                "product": product,
                "quantity": entry["quantity"],
                "line_total": line_total,
            })
            total += line_total
    return render_template("basket.html", items=items, total=total)


@app.route("/basket/add/<product_id>", methods=["POST"])
def basket_add(product_id):
    """Add a product to the basket."""
    quantity = int(request.form.get("quantity", 1))
    db.add_to_basket(_session_id(), product_id, quantity)
    return redirect(request.referrer or url_for("index"))


@app.route("/basket/remove/<product_id>", methods=["POST"])
def basket_remove(product_id):
    """Remove a product from the basket."""
    db.remove_from_basket(_session_id(), product_id)
    return redirect(url_for("basket"))


@app.route("/basket/update/<product_id>", methods=["POST"])
def basket_update(product_id):
    """Update quantity of a product in the basket."""
    quantity = int(request.form.get("quantity", 1))
    db.update_basket_quantity(_session_id(), product_id, quantity)
    return redirect(url_for("basket"))


# ---------------------------------------------------------------------------
# Checkout – Criterion 5.2
# ---------------------------------------------------------------------------


@app.route("/checkout", methods=["GET", "POST"])
def checkout_page():
    """Checkout form and transaction processing."""
    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        address = request.form.get("address", "")

        if not name or not email or not address:
            return render_template(
                "checkout.html",
                error="Please fill in all fields.",
            )

        order_id, error = db.checkout(
            _session_id(), name, email, address
        )
        if error:
            return render_template("checkout.html", error=error)

        return render_template(
            "order_confirmation.html", order_id=order_id
        )

    return render_template("checkout.html", error=None)


# ---------------------------------------------------------------------------
# Seed and run
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    db.seed_db()
    app.run(debug=True)
