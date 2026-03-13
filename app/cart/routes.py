"""Cart (basket) blueprint – add, update, remove items."""

from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId

from app import db

cart_bp = Blueprint("cart", __name__, template_folder="../templates/cart")


@cart_bp.route("/")
@login_required
def view():
    """Display the user's shopping cart."""
    basket = db.baskets.find_one({"user_id": current_user.get_id_object()})
    items = []
    total = 0
    if basket and basket.get("items"):
        for entry in basket["items"]:
            product = db.products.find_one({"_id": entry["product_id"]})
            if product:
                subtotal = product["price"] * entry["quantity"]
                total += subtotal
                items.append({
                    "product": product,
                    "quantity": entry["quantity"],
                    "subtotal": round(subtotal, 2),
                })
    return render_template("cart.html", items=items, total=round(total, 2))


@cart_bp.route("/add/<product_id>", methods=["POST"])
@login_required
def add(product_id):
    """Add a product to the cart."""
    qty = max(int(request.form.get("quantity", 1)), 1)
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()

    product = db.products.find_one({"_id": pid})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products.catalog"))

    basket = db.baskets.find_one({"user_id": uid})
    if basket:
        existing = next((i for i in basket["items"] if i["product_id"] == pid), None)
        if existing:
            db.baskets.update_one(
                {"user_id": uid, "items.product_id": pid},
                {"$inc": {"items.$.quantity": qty}, "$set": {"last_updated": datetime.now(timezone.utc)}},
            )
        else:
            db.baskets.update_one(
                {"user_id": uid},
                {"$push": {"items": {"product_id": pid, "quantity": qty}},
                 "$set": {"last_updated": datetime.now(timezone.utc)}},
            )
    else:
        db.baskets.insert_one({
            "user_id": uid,
            "items": [{"product_id": pid, "quantity": qty}],
            "last_updated": datetime.now(timezone.utc),
        })

    flash(f"Added {product['name']} to cart.", "success")
    return redirect(request.referrer or url_for("cart.view"))


@cart_bp.route("/update/<product_id>", methods=["POST"])
@login_required
def update(product_id):
    """Update the quantity of a cart item."""
    qty = int(request.form.get("quantity", 1))
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()

    if qty < 1:
        db.baskets.update_one(
            {"user_id": uid},
            {"$pull": {"items": {"product_id": pid}}, "$set": {"last_updated": datetime.now(timezone.utc)}},
        )
    else:
        db.baskets.update_one(
            {"user_id": uid, "items.product_id": pid},
            {"$set": {"items.$.quantity": qty, "last_updated": datetime.now(timezone.utc)}},
        )

    flash("Cart updated.", "success")
    return redirect(url_for("cart.view"))


@cart_bp.route("/remove/<product_id>", methods=["POST"])
@login_required
def remove(product_id):
    """Remove an item from the cart."""
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()
    db.baskets.update_one(
        {"user_id": uid},
        {"$pull": {"items": {"product_id": pid}}, "$set": {"last_updated": datetime.now(timezone.utc)}},
    )
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart.view"))
