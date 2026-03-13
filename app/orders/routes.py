"""Orders blueprint – checkout with MongoDB transactions and order history."""

from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId

from app import db, mongo_client

# NEW: basic server-side logging of checkout errors
import logging

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__, template_folder="../templates/orders")


@orders_bp.route("/")
@login_required
def history():
    """Display the user's order history."""
    user_orders = list(
        db.orders.find({"user_id": current_user.get_id_object()}).sort("order_date", -1)
    )
    return render_template("history.html", orders=user_orders)


@orders_bp.route("/<order_id>")
@login_required
def detail(order_id):
    """Display a single order's details."""
    order = db.orders.find_one({
        "_id": ObjectId(order_id),
        "user_id": current_user.get_id_object(),
    })
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.history"))
    return render_template("order_detail.html", order=order)


@orders_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """
    Checkout process using a MongoDB transaction (LB2 criterion 5.2):
    1. Verify stock for every basket item
    2. Reduce stock quantities
    3. Create order document with snapshot data
    4. Clear the basket
    All steps run inside a single transaction for atomicity.
    """
    # IMPORTANT: always use the user ObjectId consistently
    uid = ObjectId(current_user.get_id())

    # Load basket (outside tx for GET render)
    basket = db.baskets.find_one({"user_id": uid})

    if not basket or not basket.get("items"):
        flash("Your cart is empty.", "info")
        return redirect(url_for("cart.view"))

    # Load basket items for display / processing
    cart_items = []
    total = 0
    for entry in basket["items"]:
        product = db.products.find_one({"_id": entry["product_id"]})
        if product:
            subtotal = product["price"] * entry["quantity"]
            total += subtotal
            cart_items.append({
                "product": product,
                "quantity": entry["quantity"],
                "subtotal": round(subtotal, 2),
            })
    total = round(total, 2)

    if request.method == "GET":
        user_doc = db.users.find_one({"_id": uid})
        return render_template("checkout.html", items=cart_items, total=total, user=user_doc)

    # POST – process the order
    street = request.form.get("street", "").strip()
    city = request.form.get("city", "").strip()
    zip_code = request.form.get("zip_code", "").strip()
    country = request.form.get("country", "").strip()

    if not all([street, city, zip_code, country]):
        flash("Please fill in your shipping address.", "error")
        user_doc = db.users.find_one({"_id": uid})
        return render_template("checkout.html", items=cart_items, total=total, user=user_doc)

    # --- MongoDB Transaction ---
    try:
        with mongo_client.start_session() as session:
            try:
                with session.start_transaction():
                    # Re-load basket inside the transaction/session to ensure we use the same snapshot
                    basket = db.baskets.find_one({"user_id": uid}, session=session)
                    if not basket or not basket.get("items"):
                        raise ValueError("Your cart is empty.")

                    # 1. Verify stock & build order items with snapshot data
                    order_items = []
                    for entry in basket["items"]:
                        product = db.products.find_one({"_id": entry["product_id"]}, session=session)
                        if not product:
                            raise ValueError("Product no longer exists.")
                        if product.get("stock_quantity", 0) < entry.get("quantity", 0):
                            raise ValueError(
                                f"Not enough stock for {product.get('name','(unknown)')} "
                                f"(available: {product.get('stock_quantity',0)}, requested: {entry.get('quantity',0)})."
                            )
                        order_items.append({
                            "product_id": product["_id"],
                            "name_at_purchase": product["name"],
                            "price_at_purchase": product["price"],
                            "quantity": entry["quantity"],
                        })

                    # 2. Reduce stock
                    for item in order_items:
                        db.products.update_one(
                            {"_id": item["product_id"]},
                            {"$inc": {"stock_quantity": -item["quantity"]}},
                            session=session,
                        )

                    # 3. Create order (snapshot principle – LB2 5.2)
                    order_doc = {
                        "user_id": uid,
                        "order_date": datetime.now(timezone.utc),
                        "total_price": total,
                        "status": "confirmed",
                        "shipping_address": {
                            "street": street,
                            "city": city,
                            "zip_code": zip_code,
                            "country": country,
                        },
                        "order_items": order_items,
                    }
                    db.orders.insert_one(order_doc, session=session)

                    # 4. Clear basket
                    db.baskets.delete_one({"user_id": uid}, session=session)

            except Exception as tx_err:
                # Standalone MongoDB (no replica set) does not support transactions.
                # Fallback to a best-effort non-transactional checkout so the app works locally.
                if "Transaction numbers are only allowed" not in str(tx_err):
                    raise

                logger.warning("Transactions unsupported (standalone MongoDB). Falling back to non-transaction checkout.")

                # Re-load basket without session
                basket = db.baskets.find_one({"user_id": uid})
                if not basket or not basket.get("items"):
                    raise ValueError("Your cart is empty.")

                # Verify stock & build order items
                order_items = []
                for entry in basket["items"]:
                    product = db.products.find_one({"_id": entry["product_id"]})
                    if not product:
                        raise ValueError("Product no longer exists.")
                    if product.get("stock_quantity", 0) < entry.get("quantity", 0):
                        raise ValueError(
                            f"Not enough stock for {product.get('name','(unknown)')} "
                            f"(available: {product.get('stock_quantity',0)}, requested: {entry.get('quantity',0)})."
                        )
                    order_items.append({
                        "product_id": product["_id"],
                        "name_at_purchase": product["name"],
                        "price_at_purchase": product["price"],
                        "quantity": entry["quantity"],
                    })

                # Reduce stock (non-atomic)
                for item in order_items:
                    db.products.update_one(
                        {"_id": item["product_id"]},
                        {"$inc": {"stock_quantity": -item["quantity"]}},
                    )

                order_doc = {
                    "user_id": uid,
                    "order_date": datetime.now(timezone.utc),
                    "total_price": total,
                    "status": "confirmed",
                    "shipping_address": {
                        "street": street,
                        "city": city,
                        "zip_code": zip_code,
                        "country": country,
                    },
                    "order_items": order_items,
                }
                db.orders.insert_one(order_doc)
                db.baskets.delete_one({"user_id": uid})

        flash("Order placed successfully!", "success")
        return redirect(url_for("orders.history"))

    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("cart.view"))
    except Exception as e:
        logger.exception("Checkout failed")
        flash("Something went wrong during checkout. Please try again.", "error")
        return redirect(url_for("cart.view"))
