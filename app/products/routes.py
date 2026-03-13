"""Products blueprint – catalog, detail, search and filtering."""

import math
from flask import Blueprint, render_template, request

from app import db
from bson import ObjectId

products_bp = Blueprint("products", __name__, template_folder="../templates/products")

PER_PAGE = 12


@products_bp.route("/")
def catalog():
    """Product listing with filters, search and sorting."""
    # --- Filters ---
    category = request.args.get("category", "")
    brand = request.args.get("brand", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")
    search = request.args.get("q", "").strip()
    sort_by = request.args.get("sort", "newest")
    page = max(int(request.args.get("page", 1)), 1)

    query = {}
    if category:
        query["category"] = category
    if brand:
        query["brand"] = brand
    if min_price or max_price:
        price_q = {}
        if min_price:
            price_q["$gte"] = float(min_price)
        if max_price:
            price_q["$lte"] = float(max_price)
        query["price"] = price_q
    if search:
        query["$text"] = {"$search": search}

    # --- Sorting ---
    sort_map = {
        "newest": ("created_at", -1),
        "price_asc": ("price", 1),
        "price_desc": ("price", -1),
        "name_asc": ("name", 1),
    }
    sort_field, sort_dir = sort_map.get(sort_by, ("created_at", -1))

    total = db.products.count_documents(query)
    total_pages = max(math.ceil(total / PER_PAGE), 1)
    products = list(
        db.products.find(query)
        .sort(sort_field, sort_dir)
        .skip((page - 1) * PER_PAGE)
        .limit(PER_PAGE)
    )

    # Sidebar data
    categories = sorted(db.products.distinct("category"))
    brands = sorted(db.products.distinct("brand"))

    return render_template(
        "catalog.html",
        products=products,
        categories=categories,
        brands=brands,
        current_category=category,
        current_brand=brand,
        min_price=min_price,
        max_price=max_price,
        search=search,
        sort_by=sort_by,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@products_bp.route("/<product_id>")
def detail(product_id):
    """Product detail page."""
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return render_template("404.html"), 404

    reviews = list(db.reviews.find({"product_id": ObjectId(product_id)}).sort("created_at", -1))
    # Attach usernames
    for r in reviews:
        user = db.users.find_one({"_id": r["user_id"]}, {"username": 1})
        r["username"] = user["username"] if user else "Deleted User"

    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r["rating"] for r in reviews) / len(reviews), 1)

    related = list(db.products.find(
        {"category": product["category"], "_id": {"$ne": product["_id"]}}
    ).limit(4))

    return render_template(
        "detail.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=len(reviews),
        related=related,
    )
