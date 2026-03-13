"""Admin blueprint -- product CRUD, category and order management (role-protected)."""

from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from bson import ObjectId

from app import db

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")

# All available product categories
CATEGORIES = [
    "CPU", "GPU", "Monitor", "Motherboard", "PSU",
    "RAM", "Case", "Storage", "Cooling", "Peripherals",
]


def admin_required(f):
    """Decorator that ensures the current user is an admin."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/")
@admin_required
def dashboard():
    """Admin dashboard overview."""
    stats = {
        "products": db.products.count_documents({}),
        "users": db.users.count_documents({}),
        "orders": db.orders.count_documents({}),
        "reviews": db.reviews.count_documents({}),
    }
    recent_orders = list(db.orders.find().sort("order_date", -1).limit(5))
    return render_template("dashboard.html", stats=stats, recent_orders=recent_orders)


@admin_bp.route("/products")
@admin_required
def product_list():
    """List all products for admin management with search/filter support."""
    products = list(db.products.find().sort("name", 1))
    return render_template(
        "admin_products.html",
        products=products,
        categories=CATEGORIES,
    )


@admin_bp.route("/products/create", methods=["GET", "POST"])
@admin_required
def product_create():
    """Create a new product."""
    if request.method == "POST":
        product = _extract_product_form(request)
        db.products.insert_one(product)
        flash("Product created.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin_product_form.html", product=None, categories=CATEGORIES)


@admin_bp.route("/products/edit/<product_id>", methods=["GET", "POST"])
@admin_required
def product_edit(product_id):
    """Edit an existing product."""
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin.product_list"))

    if request.method == "POST":
        updated = _extract_product_form(request)
        db.products.update_one({"_id": ObjectId(product_id)}, {"$set": updated})
        flash("Product updated.", "success")
        return redirect(url_for("admin.product_list"))

    return render_template("admin_product_form.html", product=product, categories=CATEGORIES)


@admin_bp.route("/products/delete/<product_id>", methods=["POST"])
@admin_required
def product_delete(product_id):
    """Delete a product."""
    db.products.delete_one({"_id": ObjectId(product_id)})
    flash("Product deleted.", "success")
    return redirect(url_for("admin.product_list"))


@admin_bp.route("/orders")
@admin_required
def order_list():
    """List all orders with customer information."""
    orders = list(db.orders.find().sort("order_date", -1))
    # Attach user info to each order for display in admin
    for order in orders:
        user = db.users.find_one({"_id": order.get("user_id")})
        if user:
            order["user_info"] = {
                "username": user.get("username", "Unknown"),
                "email": user.get("email", ""),
            }
        else:
            order["user_info"] = None
    return render_template("admin_orders.html", orders=orders)


@admin_bp.route("/orders/<order_id>/status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    """Update an order's status (Confirmed -> Shipped -> Delivered)."""
    new_status = request.form.get("status", "confirmed")
    db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": new_status}})
    flash("Order status updated.", "success")
    return redirect(url_for("admin.order_list"))


def _extract_product_form(req):
    """Extract product data from a form submission."""
    # Parse specs from dynamic form fields
    spec_keys = req.form.getlist("spec_key")
    spec_vals = req.form.getlist("spec_value")
    specs = {}
    for k, v in zip(spec_keys, spec_vals):
        k = k.strip()
        v = v.strip()
        if k and v:
            # Try to convert numeric values
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
            specs[k] = v

    images = [u.strip() for u in req.form.get("images", "").split(",") if u.strip()]
    if not images:
        images = ["/static/images/products/placeholder.jpg"]

    return {
        "name": req.form.get("name", "").strip(),
        "brand": req.form.get("brand", "").strip(),
        "price": round(float(req.form.get("price", 0)), 2),
        "category": req.form.get("category", ""),
        "stock_quantity": int(req.form.get("stock_quantity", 0)),
        "images": images,
        "description": req.form.get("description", "").strip(),
        "specs": specs,
        "created_at": datetime.now(timezone.utc),
    }
