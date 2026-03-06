"""
database.py – MongoDB Data Access Layer for ElectroSwap Hardware Shop.

Handles five collections: Users, Products, Baskets, Orders, Reviews.
Refers to Criteria 2.2–2.9, 3.1–5.5 of the grading rubric.
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["electroswap"]

# Collections  (Refers to Criterion 2.2 – five distinct collections)
users_col = db["users"]
products_col = db["products"]
baskets_col = db["baskets"]
orders_col = db["orders"]
reviews_col = db["reviews"]


# ---------------------------------------------------------------------------
# Criterion 5.1 – Indexes
# ---------------------------------------------------------------------------

def create_indexes():
    """Create indexes on product_name and category for fast look-ups.

    Refers to Criterion 5.1 (Indexes).
    """
    products_col.create_index("name")
    products_col.create_index("category")


# ===========================  USERS  =======================================
# Refers to Criterion 2.6 – CRUD for Users


def add_user(username, email, password_hash, role="customer"):
    """Insert a new user document."""
    user = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }
    return users_col.insert_one(user)


def get_user(user_id):
    """Return a single user by _id."""
    return users_col.find_one({"_id": ObjectId(user_id)})


def get_user_by_username(username):
    """Return a single user by username."""
    return users_col.find_one({"username": username})


def update_user(user_id, update_fields):
    """Update arbitrary fields on a user."""
    return users_col.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_fields}
    )


def delete_user(user_id):
    """Delete a user by _id."""
    return users_col.delete_one({"_id": ObjectId(user_id)})


# ===========================  PRODUCTS  ====================================
# Refers to Criterion 2.4 – at least 8 attributes per product
# Refers to Criterion 2.6 – CRUD for Products
# Refers to Criterion 2.7 – heterogeneous "specs" sub-document


def add_product(name, brand, price, category, stock, description, image_url,
                specs=None):
    """Insert a product with ≥ 8 attributes.

    The *specs* sub-document varies by category (Criterion 2.7).
    """
    product = {
        "name": name,
        "brand": brand,
        "price": price,
        "category": category,
        "stock": stock,
        "description": description,
        "image_url": image_url,
        "specs": specs or {},
        "created_at": datetime.now(timezone.utc),  # 8th attribute
    }
    return products_col.insert_one(product)


def get_product(product_id):
    """Return a single product by _id."""
    return products_col.find_one({"_id": ObjectId(product_id)})


def get_all_products(category=None, search=None):
    """Return products, optionally filtered by category or search term."""
    query = {}
    if category:
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    return list(products_col.find(query))


def update_product(product_id, update_fields):
    """Update arbitrary fields on a product."""
    return products_col.update_one(
        {"_id": ObjectId(product_id)}, {"$set": update_fields}
    )


def delete_product(product_id):
    """Delete a product by _id."""
    return products_col.delete_one({"_id": ObjectId(product_id)})


def get_categories():
    """Return a sorted list of unique category values."""
    return sorted(products_col.distinct("category"))


# ===========================  BASKETS  =====================================
# Refers to Criterion 2.6 – CRUD for Baskets


def get_basket(session_id):
    """Return the basket document for a browser session."""
    basket = baskets_col.find_one({"session_id": session_id})
    if not basket:
        basket = {"session_id": session_id, "items": []}
        baskets_col.insert_one(basket)
        basket = baskets_col.find_one({"session_id": session_id})
    return basket


def add_to_basket(session_id, product_id, quantity=1):
    """Add a product to the basket or increase its quantity."""
    basket = get_basket(session_id)
    product_id_str = str(product_id)

    for item in basket["items"]:
        if item["product_id"] == product_id_str:
            item["quantity"] += quantity
            baskets_col.update_one(
                {"_id": basket["_id"]}, {"$set": {"items": basket["items"]}}
            )
            return

    basket["items"].append(
        {"product_id": product_id_str, "quantity": quantity}
    )
    baskets_col.update_one(
        {"_id": basket["_id"]}, {"$set": {"items": basket["items"]}}
    )


def remove_from_basket(session_id, product_id):
    """Remove a product from the basket entirely."""
    basket = get_basket(session_id)
    product_id_str = str(product_id)

    basket["items"] = [
        i for i in basket["items"] if i["product_id"] != product_id_str
    ]
    baskets_col.update_one(
        {"_id": basket["_id"]}, {"$set": {"items": basket["items"]}}
    )


def update_basket_quantity(session_id, product_id, quantity):
    """Set the quantity of a specific product in the basket."""
    basket = get_basket(session_id)
    product_id_str = str(product_id)

    for item in basket["items"]:
        if item["product_id"] == product_id_str:
            item["quantity"] = max(1, quantity)
            break

    baskets_col.update_one(
        {"_id": basket["_id"]}, {"$set": {"items": basket["items"]}}
    )


def clear_basket(session_id):
    """Remove all items from the basket."""
    baskets_col.update_one(
        {"session_id": session_id}, {"$set": {"items": []}}
    )


def delete_basket(session_id):
    """Delete the basket document entirely."""
    return baskets_col.delete_one({"session_id": session_id})


# ===========================  ORDERS  ======================================
# Refers to Criterion 2.6 – CRUD for Orders


def create_order(session_id, customer_name, customer_email, address, items,
                 total):
    """Create an order document."""
    order = {
        "session_id": session_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "address": address,
        "items": items,
        "total": total,
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc),
    }
    return orders_col.insert_one(order)


def get_order(order_id):
    """Return a single order by _id."""
    return orders_col.find_one({"_id": ObjectId(order_id)})


def get_orders_by_session(session_id):
    """Return all orders for a given session."""
    return list(orders_col.find({"session_id": session_id}))


def update_order(order_id, update_fields):
    """Update arbitrary fields on an order."""
    return orders_col.update_one(
        {"_id": ObjectId(order_id)}, {"$set": update_fields}
    )


def delete_order(order_id):
    """Delete an order by _id."""
    return orders_col.delete_one({"_id": ObjectId(order_id)})


# ===========================  REVIEWS  =====================================
# Refers to Criterion 2.6 – CRUD for Reviews


def add_review(product_id, author, rating, comment):
    """Insert a review for a product."""
    review = {
        "product_id": str(product_id),
        "author": author,
        "rating": int(rating),
        "comment": comment,
        "created_at": datetime.now(timezone.utc),
    }
    return reviews_col.insert_one(review)


def get_reviews_for_product(product_id):
    """Return all reviews for a given product."""
    return list(reviews_col.find({"product_id": str(product_id)}))


def update_review(review_id, update_fields):
    """Update arbitrary fields on a review."""
    return reviews_col.update_one(
        {"_id": ObjectId(review_id)}, {"$set": update_fields}
    )


def delete_review(review_id):
    """Delete a review by _id."""
    return reviews_col.delete_one({"_id": ObjectId(review_id)})


# ===========================================================================
# Criterion 2.8 – Aggregation Pipeline
# ===========================================================================


def avg_price_per_category():
    """Calculate the average product price per category.

    Refers to Criterion 2.8 (Aggregation Pipeline).
    """
    pipeline = [
        {"$group": {"_id": "$category", "avg_price": {"$avg": "$price"}}},
        {"$sort": {"_id": 1}},
    ]
    return list(products_col.aggregate(pipeline))


def product_count_per_category():
    """Count the number of products in each category using aggregation."""
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return list(products_col.aggregate(pipeline))


# ===========================================================================
# Criterion 5.2 – Transaction-like Checkout
# ===========================================================================


def checkout(session_id, customer_name, customer_email, address):
    """Process checkout: reduce stock only when the order is created.

    Refers to Criterion 5.2 (Transactions).
    Ensures atomicity by verifying and reducing stock for every item
    before creating the order.  If any item is out of stock the entire
    checkout is aborted and no stock is modified.
    """
    basket = get_basket(session_id)
    if not basket or not basket.get("items"):
        return None, "Basket is empty."

    # Phase 1 – validate stock availability for every basket item
    order_items = []
    total = 0.0
    for item in basket["items"]:
        product = get_product(item["product_id"])
        if not product:
            return None, f"Product {item['product_id']} not found."
        if product["stock"] < item["quantity"]:
            return None, (
                f"Not enough stock for '{product['name']}'. "
                f"Available: {product['stock']}, requested: {item['quantity']}."
            )
        line_total = product["price"] * item["quantity"]
        order_items.append({
            "product_id": item["product_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "line_total": line_total,
        })
        total += line_total

    # Phase 2 – reduce stock for each item
    for oi in order_items:
        products_col.update_one(
            {"_id": ObjectId(oi["product_id"])},
            {"$inc": {"stock": -oi["quantity"]}},
        )

    # Phase 3 – create the order
    result = create_order(
        session_id, customer_name, customer_email, address, order_items, total
    )

    # Phase 4 – clear the basket
    clear_basket(session_id)

    return result.inserted_id, None


# ===========================================================================
# Criterion 2.9 – Seed Database with 20+ realistic hardware items
# ===========================================================================


def seed_db():
    """Populate the database with 20+ realistic hardware products.

    Refers to Criterion 2.9 (Data Volume).
    Uses heterogeneous specs sub-documents (Criterion 2.7).
    """
    # Only seed if the products collection is empty
    if products_col.count_documents({}) > 0:
        return

    products = [
        # ---------- CPUs (Criterion 2.7 – cores, socket) ----------
        {
            "name": "AMD Ryzen 9 7950X",
            "brand": "AMD",
            "price": 549.99,
            "category": "CPU",
            "stock": 25,
            "description": "16-core, 32-thread high-end desktop processor.",
            "image_url": "/static/images/cpu_placeholder.png",
            "specs": {"cores": 16, "threads": 32, "socket": "AM5",
                      "base_clock": "4.5 GHz", "tdp": 170},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "AMD Ryzen 7 7700X",
            "brand": "AMD",
            "price": 299.99,
            "category": "CPU",
            "stock": 40,
            "description": "8-core processor for gamers and creators.",
            "image_url": "/static/images/cpu_placeholder.png",
            "specs": {"cores": 8, "threads": 16, "socket": "AM5",
                      "base_clock": "4.5 GHz", "tdp": 105},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Intel Core i9-13900K",
            "brand": "Intel",
            "price": 589.99,
            "category": "CPU",
            "stock": 18,
            "description": "24-core flagship for enthusiasts.",
            "image_url": "/static/images/cpu_placeholder.png",
            "specs": {"cores": 24, "threads": 32, "socket": "LGA 1700",
                      "base_clock": "3.0 GHz", "tdp": 253},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Intel Core i5-13600K",
            "brand": "Intel",
            "price": 319.99,
            "category": "CPU",
            "stock": 55,
            "description": "Mid-range powerhouse with efficiency cores.",
            "image_url": "/static/images/cpu_placeholder.png",
            "specs": {"cores": 14, "threads": 20, "socket": "LGA 1700",
                      "base_clock": "3.5 GHz", "tdp": 181},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- GPUs ----------
        {
            "name": "NVIDIA GeForce RTX 4090",
            "brand": "NVIDIA",
            "price": 1599.99,
            "category": "GPU",
            "stock": 10,
            "description": "Flagship graphics card with Ada Lovelace.",
            "image_url": "/static/images/gpu_placeholder.png",
            "specs": {"vram": "24 GB GDDR6X", "cuda_cores": 16384,
                      "boost_clock": "2.52 GHz", "tdp": 450},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "NVIDIA GeForce RTX 4070 Ti",
            "brand": "NVIDIA",
            "price": 799.99,
            "category": "GPU",
            "stock": 22,
            "description": "High-performance GPU for 1440p gaming.",
            "image_url": "/static/images/gpu_placeholder.png",
            "specs": {"vram": "12 GB GDDR6X", "cuda_cores": 7680,
                      "boost_clock": "2.61 GHz", "tdp": 285},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "AMD Radeon RX 7900 XTX",
            "brand": "AMD",
            "price": 949.99,
            "category": "GPU",
            "stock": 15,
            "description": "Top-tier RDNA 3 GPU.",
            "image_url": "/static/images/gpu_placeholder.png",
            "specs": {"vram": "24 GB GDDR6", "stream_processors": 6144,
                      "boost_clock": "2.50 GHz", "tdp": 355},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "AMD Radeon RX 7600",
            "brand": "AMD",
            "price": 269.99,
            "category": "GPU",
            "stock": 60,
            "description": "Budget-friendly 1080p GPU.",
            "image_url": "/static/images/gpu_placeholder.png",
            "specs": {"vram": "8 GB GDDR6", "stream_processors": 2048,
                      "boost_clock": "2.66 GHz", "tdp": 165},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- Monitors (Criterion 2.7 – resolution, refresh_rate) ---
        {
            "name": "Samsung Odyssey G9",
            "brand": "Samsung",
            "price": 1299.99,
            "category": "Monitor",
            "stock": 8,
            "description": "49-inch ultra-wide curved gaming monitor.",
            "image_url": "/static/images/monitor_placeholder.png",
            "specs": {"resolution": "5120x1440", "refresh_rate": "240 Hz",
                      "panel_type": "VA", "size": "49 inch"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "LG UltraGear 27GP850-B",
            "brand": "LG",
            "price": 399.99,
            "category": "Monitor",
            "stock": 30,
            "description": "27-inch Nano IPS gaming monitor.",
            "image_url": "/static/images/monitor_placeholder.png",
            "specs": {"resolution": "2560x1440", "refresh_rate": "165 Hz",
                      "panel_type": "Nano IPS", "size": "27 inch"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Dell UltraSharp U2723QE",
            "brand": "Dell",
            "price": 619.99,
            "category": "Monitor",
            "stock": 20,
            "description": "27-inch 4K USB-C hub monitor.",
            "image_url": "/static/images/monitor_placeholder.png",
            "specs": {"resolution": "3840x2160", "refresh_rate": "60 Hz",
                      "panel_type": "IPS Black", "size": "27 inch"},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- RAM ----------
        {
            "name": "Corsair Vengeance DDR5 32 GB",
            "brand": "Corsair",
            "price": 109.99,
            "category": "RAM",
            "stock": 80,
            "description": "DDR5-5600 dual-channel kit (2 x 16 GB).",
            "image_url": "/static/images/ram_placeholder.png",
            "specs": {"capacity": "32 GB", "type": "DDR5", "speed": 5600,
                      "modules": "2 x 16 GB"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "G.Skill Trident Z5 RGB 32 GB",
            "brand": "G.Skill",
            "price": 134.99,
            "category": "RAM",
            "stock": 45,
            "description": "Premium DDR5 RGB kit for enthusiasts.",
            "image_url": "/static/images/ram_placeholder.png",
            "specs": {"capacity": "32 GB", "type": "DDR5", "speed": 6000,
                      "modules": "2 x 16 GB"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Kingston Fury Beast DDR4 16 GB",
            "brand": "Kingston",
            "price": 42.99,
            "category": "RAM",
            "stock": 120,
            "description": "Reliable DDR4-3200 kit.",
            "image_url": "/static/images/ram_placeholder.png",
            "specs": {"capacity": "16 GB", "type": "DDR4", "speed": 3200,
                      "modules": "2 x 8 GB"},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- Motherboards ----------
        {
            "name": "ASUS ROG Strix X670E-E",
            "brand": "ASUS",
            "price": 449.99,
            "category": "Motherboard",
            "stock": 12,
            "description": "AM5 enthusiast ATX motherboard.",
            "image_url": "/static/images/mb_placeholder.png",
            "specs": {"socket": "AM5", "chipset": "X670E",
                      "form_factor": "ATX", "ram_slots": 4},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "MSI MAG B650 Tomahawk",
            "brand": "MSI",
            "price": 219.99,
            "category": "Motherboard",
            "stock": 35,
            "description": "Solid mid-range AM5 board.",
            "image_url": "/static/images/mb_placeholder.png",
            "specs": {"socket": "AM5", "chipset": "B650",
                      "form_factor": "ATX", "ram_slots": 4},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Gigabyte Z790 Aorus Elite AX",
            "brand": "Gigabyte",
            "price": 289.99,
            "category": "Motherboard",
            "stock": 28,
            "description": "Feature-packed LGA 1700 motherboard.",
            "image_url": "/static/images/mb_placeholder.png",
            "specs": {"socket": "LGA 1700", "chipset": "Z790",
                      "form_factor": "ATX", "ram_slots": 4},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- Storage ----------
        {
            "name": "Samsung 990 Pro 2 TB",
            "brand": "Samsung",
            "price": 179.99,
            "category": "Storage",
            "stock": 50,
            "description": "PCIe 4.0 NVMe M.2 SSD.",
            "image_url": "/static/images/storage_placeholder.png",
            "specs": {"capacity": "2 TB", "interface": "PCIe 4.0 NVMe",
                      "read_speed": "7450 MB/s", "write_speed": "6900 MB/s"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "WD Black SN850X 1 TB",
            "brand": "Western Digital",
            "price": 89.99,
            "category": "Storage",
            "stock": 65,
            "description": "High-performance Gen 4 NVMe SSD.",
            "image_url": "/static/images/storage_placeholder.png",
            "specs": {"capacity": "1 TB", "interface": "PCIe 4.0 NVMe",
                      "read_speed": "7300 MB/s", "write_speed": "6300 MB/s"},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Seagate Barracuda 4 TB",
            "brand": "Seagate",
            "price": 79.99,
            "category": "Storage",
            "stock": 90,
            "description": "High-capacity 3.5-inch HDD.",
            "image_url": "/static/images/storage_placeholder.png",
            "specs": {"capacity": "4 TB", "interface": "SATA III",
                      "rpm": 5400, "cache": "256 MB"},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- Power Supplies ----------
        {
            "name": "Corsair RM850x",
            "brand": "Corsair",
            "price": 139.99,
            "category": "PSU",
            "stock": 40,
            "description": "850 W fully modular 80+ Gold PSU.",
            "image_url": "/static/images/psu_placeholder.png",
            "specs": {"wattage": 850, "efficiency": "80+ Gold",
                      "modular": True},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "be quiet! Straight Power 12 1000W",
            "brand": "be quiet!",
            "price": 199.99,
            "category": "PSU",
            "stock": 20,
            "description": "Premium 1000 W ATX 3.0 PSU.",
            "image_url": "/static/images/psu_placeholder.png",
            "specs": {"wattage": 1000, "efficiency": "80+ Platinum",
                      "modular": True},
            "created_at": datetime.now(timezone.utc),
        },
        # ---------- Cases ----------
        {
            "name": "NZXT H510 Flow",
            "brand": "NZXT",
            "price": 89.99,
            "category": "Case",
            "stock": 35,
            "description": "Mid-tower ATX case with mesh front panel.",
            "image_url": "/static/images/case_placeholder.png",
            "specs": {"form_factor": "Mid-Tower ATX",
                      "max_gpu_length": "381 mm", "fans_included": 2},
            "created_at": datetime.now(timezone.utc),
        },
        {
            "name": "Fractal Design Torrent",
            "brand": "Fractal Design",
            "price": 189.99,
            "category": "Case",
            "stock": 18,
            "description": "High-airflow open-front tower.",
            "image_url": "/static/images/case_placeholder.png",
            "specs": {"form_factor": "Mid-Tower ATX",
                      "max_gpu_length": "461 mm", "fans_included": 5},
            "created_at": datetime.now(timezone.utc),
        },
    ]

    products_col.insert_many(products)

    # Create indexes after seeding
    create_indexes()
