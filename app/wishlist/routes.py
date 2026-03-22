"""Wishlist blueprint – add, remove, move to cart."""

from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId

from app import db

wishlist_bp = Blueprint("wishlist", __name__, template_folder="../templates/wishlist")


@wishlist_bp.route("/")
@login_required
def view():
    """Display the user's wishlist."""
    wl = db.wishlists.find_one({"user_id": current_user.get_id_object()})
    items = []
    if wl and wl.get("items"):
        for entry in wl["items"]:
            product = db.products.find_one({"_id": entry["product_id"]})
            if product:
                items.append({"product": product, "added_at": entry.get("added_at")})
    return render_template("wishlist.html", items=items)


@wishlist_bp.route("/add/<product_id>", methods=["POST"])
@login_required
def add(product_id):
    """Add a product to the wishlist."""
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()

    wl = db.wishlists.find_one({"user_id": uid})
    if wl:
        if any(i["product_id"] == pid for i in wl.get("items", [])):
            flash("Already in your wishlist.", "info")
            return redirect(request.referrer or url_for("wishlist.view"))
        db.wishlists.update_one(
            {"user_id": uid},
            {"$push": {"items": {"product_id": pid, "added_at": datetime.now(timezone.utc)}}},
        )
    else:
        db.wishlists.insert_one({
            "user_id": uid,
            "name": "My Wishlist",
            "items": [{"product_id": pid, "added_at": datetime.now(timezone.utc)}],
        })

    flash("Added to wishlist.", "success")
    return redirect(request.referrer or url_for("wishlist.view"))


@wishlist_bp.route("/remove/<product_id>", methods=["POST"])
@login_required
def remove(product_id):
    """Remove an item from the wishlist."""
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()
    db.wishlists.update_one(
        {"user_id": uid},
        {"$pull": {"items": {"product_id": pid}}},
    )
    flash("Removed from wishlist.", "success")
    return redirect(url_for("wishlist.view"))


@wishlist_bp.route("/move-to-cart/<product_id>", methods=["POST"])
@login_required
def move_to_cart(product_id):
    """Move an item from the wishlist to the shopping cart."""
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()

    # Add to cart
    basket = db.baskets.find_one({"user_id": uid})
    if basket:
        existing = next((i for i in basket["items"] if i["product_id"] == pid), None)
        if existing:
            db.baskets.update_one(
                {"user_id": uid, "items.product_id": pid},
                {"$inc": {"items.$.quantity": 1}, "$set": {"last_updated": datetime.now(timezone.utc)}},
            )
        else:
            db.baskets.update_one(
                {"user_id": uid},
                {"$push": {"items": {"product_id": pid, "quantity": 1}},
                 "$set": {"last_updated": datetime.now(timezone.utc)}},
            )
    else:
        db.baskets.insert_one({
            "user_id": uid,
            "items": [{"product_id": pid, "quantity": 1}],
            "last_updated": datetime.now(timezone.utc),
        })

    # Remove from wishlist
    db.wishlists.update_one(
        {"user_id": uid},
        {"$pull": {"items": {"product_id": pid}}},
    )

    flash("Moved to cart.", "success")
    return redirect(url_for("wishlist.view"))
