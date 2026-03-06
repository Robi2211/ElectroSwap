"""Reviews blueprint – create reviews (verified purchase only)."""

from datetime import datetime, timezone
from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId

from app import db

reviews_bp = Blueprint("reviews", __name__, template_folder="../templates/reviews")


@reviews_bp.route("/add/<product_id>", methods=["POST"])
@login_required
def add(product_id):
    """Add a review for a product (only if the user bought it)."""
    pid = ObjectId(product_id)
    uid = current_user.get_id_object()

    # Check verified purchase
    purchased = db.orders.find_one({
        "user_id": uid,
        "order_items.product_id": pid,
    })
    if not purchased:
        flash("You can only review products you have purchased.", "error")
        return redirect(url_for("products.detail", product_id=product_id))

    # Check for existing review
    existing = db.reviews.find_one({"product_id": pid, "user_id": uid})
    if existing:
        flash("You have already reviewed this product.", "info")
        return redirect(url_for("products.detail", product_id=product_id))

    rating = int(request.form.get("rating", 5))
    rating = max(1, min(5, rating))
    comment = request.form.get("comment", "").strip()

    db.reviews.insert_one({
        "product_id": pid,
        "user_id": uid,
        "rating": rating,
        "comment": comment,
        "verified_purchase": True,
        "created_at": datetime.now(timezone.utc),
    })

    flash("Thank you for your review!", "success")
    return redirect(url_for("products.detail", product_id=product_id))
