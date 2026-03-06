"""
database.py – MongoDB logic for the Electro Swap hardware shop.

Collections: Users, Products, Baskets, Orders, Reviews
"""

from datetime import datetime, timezone

from bson import ObjectId
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

client = MongoClient("mongodb://localhost:27017/")
db = client["electroswap"]

users_col = db["users"]
products_col = db["products"]
baskets_col = db["baskets"]
orders_col = db["orders"]
reviews_col = db["reviews"]


# ---------------------------------------------------------------------------
# Criterion 5.1 – Indexes
# ---------------------------------------------------------------------------

def create_indexes():
    """Create indexes on 'name' and 'category' for faster queries."""
    # Criterion 5.1: Indexes on name and category
    products_col.create_index("name")
    products_col.create_index("category")
    users_col.create_index("email", unique=True)
    users_col.create_index("username", unique=True)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def register_user(username, email, password, street="", city="", zip_code=""):
    """Register a new user with a hashed password."""
    if users_col.find_one({"$or": [{"username": username}, {"email": email}]}):
        return None  # already exists
    user = {
        "username": username,
        "email": email,
        # Criterion 2.5: Werkzeug password hashing
        "password_hash": generate_password_hash(password),
        "address": {"street": street, "city": city, "zip": zip_code},
        "role": "customer",
        "created_at": datetime.now(timezone.utc),
    }
    result = users_col.insert_one(user)
    return result.inserted_id


def authenticate_user(email, password):
    """Return user document if credentials are valid, else None."""
    user = users_col.find_one({"email": email})
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def get_user(user_id):
    """Return a user document by _id."""
    return users_col.find_one({"_id": ObjectId(user_id)})


# ---------------------------------------------------------------------------
# Product helpers
# ---------------------------------------------------------------------------

def get_products(search=None, category=None):
    """Return products, optionally filtered by search term or category."""
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if category:
        query["category"] = category
    return list(products_col.find(query))


def get_product(product_id):
    """Return a single product by _id."""
    return products_col.find_one({"_id": ObjectId(product_id)})


def get_categories():
    """Return a sorted list of distinct categories."""
    return sorted(products_col.distinct("category"))


# ---------------------------------------------------------------------------
# Basket helpers
# ---------------------------------------------------------------------------

def get_basket(user_id):
    """Return the basket document for a user (or None)."""
    return baskets_col.find_one({"user_id": ObjectId(user_id)})


def add_to_basket(user_id, product_id, quantity=1):
    """Add a product to the user's basket or increase quantity."""
    uid = ObjectId(user_id)
    pid = ObjectId(product_id)
    basket = baskets_col.find_one({"user_id": uid})
    if not basket:
        baskets_col.insert_one({
            "user_id": uid,
            "items": [{"product_id": pid, "quantity": quantity}],
        })
        return
    # Check if product already in basket
    for item in basket.get("items", []):
        if item["product_id"] == pid:
            baskets_col.update_one(
                {"user_id": uid, "items.product_id": pid},
                {"$inc": {"items.$.quantity": quantity}},
            )
            return
    baskets_col.update_one(
        {"user_id": uid},
        {"$push": {"items": {"product_id": pid, "quantity": quantity}}},
    )


def remove_from_basket(user_id, product_id):
    """Remove a product from the user's basket."""
    baskets_col.update_one(
        {"user_id": ObjectId(user_id)},
        {"$pull": {"items": {"product_id": ObjectId(product_id)}}},
    )


def update_basket_quantity(user_id, product_id, quantity):
    """Set the quantity for a product in the basket."""
    if quantity <= 0:
        remove_from_basket(user_id, product_id)
        return
    baskets_col.update_one(
        {"user_id": ObjectId(user_id), "items.product_id": ObjectId(product_id)},
        {"$set": {"items.$.quantity": quantity}},
    )


def get_basket_details(user_id):
    """Return basket items enriched with product data and total price."""
    basket = get_basket(user_id)
    if not basket or not basket.get("items"):
        return [], 0
    items = []
    total = 0
    for entry in basket["items"]:
        product = products_col.find_one({"_id": entry["product_id"]})
        if product:
            subtotal = product["price"] * entry["quantity"]
            items.append({
                "product": product,
                "quantity": entry["quantity"],
                "subtotal": subtotal,
            })
            total += subtotal
    return items, round(total, 2)


# ---------------------------------------------------------------------------
# Criterion 5.2 – Checkout with Transaction Logic
# ---------------------------------------------------------------------------

def checkout(user_id):
    """
    Check stock -> create order (snapshot) -> reduce stock -> clear basket.

    Returns (True, order_id) on success, (False, error_message) on failure.
    """
    # Criterion 5.2: Transaction Logic
    uid = ObjectId(user_id)
    basket = baskets_col.find_one({"user_id": uid})
    if not basket or not basket.get("items"):
        return False, "Basket is empty."

    order_items = []
    for entry in basket["items"]:
        product = products_col.find_one({"_id": entry["product_id"]})
        if not product:
            return False, f"Product not found."
        if product.get("stock", 0) < entry["quantity"]:
            return False, f"Not enough stock for '{product['name']}'."
        # Criterion: Snapshot-Principle – store name & price at time of purchase
        order_items.append({
            "product_id": product["_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": entry["quantity"],
            "image": product.get("image", ""),
        })

    # Create the order
    order = {
        "user_id": uid,
        "items": order_items,
        "total": round(sum(i["price"] * i["quantity"] for i in order_items), 2),
        "status": "confirmed",
        "created_at": datetime.now(timezone.utc),
    }
    result = orders_col.insert_one(order)

    # Reduce stock
    for entry in basket["items"]:
        products_col.update_one(
            {"_id": entry["product_id"]},
            {"$inc": {"stock": -entry["quantity"]}},
        )

    # Clear the basket
    baskets_col.delete_one({"user_id": uid})

    return True, result.inserted_id


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def get_orders(user_id):
    """Return all orders for a user, newest first."""
    return list(orders_col.find({"user_id": ObjectId(user_id)}).sort("created_at", -1))


def has_purchased(user_id, product_id):
    """Check if a user has purchased a specific product."""
    return orders_col.find_one({
        "user_id": ObjectId(user_id),
        "items.product_id": ObjectId(product_id),
    }) is not None


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def add_review(user_id, product_id, rating, comment):
    """Add a review for a product."""
    review = {
        "user_id": ObjectId(user_id),
        "product_id": ObjectId(product_id),
        "rating": int(rating),
        "comment": comment,
        "created_at": datetime.now(timezone.utc),
    }
    reviews_col.insert_one(review)


def get_reviews(product_id):
    """Return all reviews for a product with usernames."""
    pipeline = [
        {"$match": {"product_id": ObjectId(product_id)}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user",
        }},
        {"$unwind": "$user"},
        {"$project": {
            "rating": 1,
            "comment": 1,
            "created_at": 1,
            "username": "$user.username",
        }},
        {"$sort": {"created_at": -1}},
    ]
    return list(reviews_col.aggregate(pipeline))


# ---------------------------------------------------------------------------
# Criterion 2.8 – Aggregation Pipeline (Analytics)
# ---------------------------------------------------------------------------

def get_analytics():
    """Calculate average price per category using the aggregation pipeline."""
    # Criterion 2.8: Aggregation Pipeline – average price per category
    pipeline = [
        {"$group": {
            "_id": "$category",
            "avg_price": {"$avg": "$price"},
            "total_products": {"$sum": 1},
            "total_stock": {"$sum": "$stock"},
        }},
        {"$sort": {"_id": 1}},
    ]
    return list(products_col.aggregate(pipeline))


def get_order_analytics():
    """Return total revenue and number of orders."""
    pipeline = [
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$total"},
            "order_count": {"$sum": 1},
        }},
    ]
    result = list(orders_col.aggregate(pipeline))
    if result:
        return result[0]
    return {"total_revenue": 0, "order_count": 0}


# ---------------------------------------------------------------------------
# Criterion 2.9 – Seed Database with 20+ realistic hardware items
# ---------------------------------------------------------------------------

def seed_db():
    """Seed the database with 20+ realistic hardware products."""
    # Criterion 2.9: 20+ realistic products
    products_col.drop()
    reviews_col.drop()

    products = [
        # --- CPUs (Criterion 2.7: Heterogeneous specs – CPU attributes) ---
        {
            "name": "AMD Ryzen 9 7950X",
            "brand": "AMD",
            "category": "CPU",
            "price": 549.99,
            "stock": 15,
            "description": "16-core, 32-thread desktop processor for enthusiasts.",
            "image": "https://source.unsplash.com/featured/?amd,cpu",
            # Criterion 2.7: Heterogeneous attributes
            "specs": {"socket": "AM5", "cores": 16, "threads": 32, "clock": "4.5 GHz", "tdp": "170W"},
        },
        {
            "name": "Intel Core i9-13900K",
            "brand": "Intel",
            "category": "CPU",
            "price": 589.99,
            "stock": 12,
            "description": "24-core (8P+16E) flagship desktop processor.",
            "image": "https://source.unsplash.com/featured/?intel,cpu",
            "specs": {"socket": "LGA1700", "cores": 24, "threads": 32, "clock": "3.0 GHz", "tdp": "125W"},
        },
        {
            "name": "AMD Ryzen 7 7800X3D",
            "brand": "AMD",
            "category": "CPU",
            "price": 349.99,
            "stock": 20,
            "description": "8-core gaming processor with 3D V-Cache technology.",
            "image": "https://source.unsplash.com/featured/?amd,processor",
            "specs": {"socket": "AM5", "cores": 8, "threads": 16, "clock": "4.2 GHz", "tdp": "120W"},
        },
        # --- GPUs ---
        {
            "name": "NVIDIA GeForce RTX 4090",
            "brand": "NVIDIA",
            "category": "GPU",
            "price": 1599.99,
            "stock": 5,
            "description": "Flagship graphics card with Ada Lovelace architecture.",
            "image": "https://source.unsplash.com/featured/?nvidia,gpu",
            # Criterion 2.7: Different specs for GPU
            "specs": {"vram": "24 GB GDDR6X", "cuda_cores": 16384, "boost_clock": "2520 MHz", "bus_width": "384-bit"},
        },
        {
            "name": "AMD Radeon RX 7900 XTX",
            "brand": "AMD",
            "category": "GPU",
            "price": 949.99,
            "stock": 8,
            "description": "High-end RDNA 3 graphics card for 4K gaming.",
            "image": "https://source.unsplash.com/featured/?amd,graphics+card",
            "specs": {"vram": "24 GB GDDR6", "stream_processors": 6144, "boost_clock": "2500 MHz", "bus_width": "384-bit"},
        },
        {
            "name": "NVIDIA GeForce RTX 4070 Ti",
            "brand": "NVIDIA",
            "category": "GPU",
            "price": 799.99,
            "stock": 10,
            "description": "Excellent 1440p performance with DLSS 3.",
            "image": "https://source.unsplash.com/featured/?nvidia,graphics",
            "specs": {"vram": "12 GB GDDR6X", "cuda_cores": 7680, "boost_clock": "2610 MHz", "bus_width": "192-bit"},
        },
        # --- SSDs (Criterion 2.7: Heterogeneous specs – SSD attributes) ---
        {
            "name": "Samsung 990 Pro 2TB",
            "brand": "Samsung",
            "category": "SSD",
            "price": 179.99,
            "stock": 30,
            "description": "PCIe 4.0 NVMe M.2 SSD with top-tier performance.",
            "image": "https://source.unsplash.com/featured/?samsung,ssd",
            "specs": {"interface": "PCIe 4.0 NVMe", "read_speed": "7450 MB/s", "write_speed": "6900 MB/s", "capacity": "2 TB"},
        },
        {
            "name": "WD Black SN850X 1TB",
            "brand": "Western Digital",
            "category": "SSD",
            "price": 89.99,
            "stock": 25,
            "description": "High-performance NVMe SSD for gaming.",
            "image": "https://source.unsplash.com/featured/?western+digital,ssd",
            "specs": {"interface": "PCIe 4.0 NVMe", "read_speed": "7300 MB/s", "write_speed": "6300 MB/s", "capacity": "1 TB"},
        },
        # --- Monitors (Criterion 2.7: Heterogeneous specs – Monitor attributes) ---
        {
            "name": "ASUS ROG Swift PG27AQN",
            "brand": "ASUS",
            "category": "Monitor",
            "price": 899.99,
            "stock": 7,
            "description": "27-inch 1440p 360Hz eSports monitor.",
            "image": "https://source.unsplash.com/featured/?asus,monitor",
            "specs": {"resolution": "2560x1440", "refresh_rate": "360 Hz", "panel_type": "IPS", "size": "27 inch"},
        },
        {
            "name": "LG UltraGear 27GP950-B",
            "brand": "LG",
            "category": "Monitor",
            "price": 649.99,
            "stock": 10,
            "description": "27-inch 4K 160Hz Nano IPS gaming monitor.",
            "image": "https://source.unsplash.com/featured/?lg,monitor",
            "specs": {"resolution": "3840x2160", "refresh_rate": "160 Hz", "panel_type": "Nano IPS", "size": "27 inch"},
        },
        {
            "name": "Dell Alienware AW3423DWF",
            "brand": "Dell",
            "category": "Monitor",
            "price": 1099.99,
            "stock": 6,
            "description": "34-inch curved QD-OLED ultrawide gaming monitor.",
            "image": "https://source.unsplash.com/featured/?dell,monitor",
            "specs": {"resolution": "3440x1440", "refresh_rate": "165 Hz", "panel_type": "QD-OLED", "size": "34 inch"},
        },
        # --- RAM ---
        {
            "name": "Corsair Dominator Platinum RGB 32GB",
            "brand": "Corsair",
            "category": "RAM",
            "price": 154.99,
            "stock": 20,
            "description": "DDR5 dual-channel kit with Corsair DHX cooling.",
            "image": "https://source.unsplash.com/featured/?corsair,ram",
            "specs": {"type": "DDR5", "speed": "6000 MHz", "capacity": "32 GB (2x16)", "latency": "CL36"},
        },
        {
            "name": "G.Skill Trident Z5 RGB 32GB",
            "brand": "G.Skill",
            "category": "RAM",
            "price": 139.99,
            "stock": 18,
            "description": "High-performance DDR5 memory with RGB lighting.",
            "image": "https://source.unsplash.com/featured/?gskill,memory",
            "specs": {"type": "DDR5", "speed": "6400 MHz", "capacity": "32 GB (2x16)", "latency": "CL32"},
        },
        # --- Motherboards ---
        {
            "name": "ASUS ROG Crosshair X670E Hero",
            "brand": "ASUS",
            "category": "Motherboard",
            "price": 699.99,
            "stock": 8,
            "description": "Premium AM5 motherboard with Wi-Fi 6E and PCIe 5.0.",
            "image": "https://source.unsplash.com/featured/?asus,motherboard",
            "specs": {"socket": "AM5", "chipset": "X670E", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5"},
        },
        {
            "name": "MSI MPG Z790 Carbon WiFi",
            "brand": "MSI",
            "category": "Motherboard",
            "price": 429.99,
            "stock": 11,
            "description": "Intel Z790 ATX motherboard with Wi-Fi 6E.",
            "image": "https://source.unsplash.com/featured/?msi,motherboard",
            "specs": {"socket": "LGA1700", "chipset": "Z790", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5"},
        },
        # --- Power Supplies ---
        {
            "name": "Corsair RM1000x (2023)",
            "brand": "Corsair",
            "category": "PSU",
            "price": 189.99,
            "stock": 14,
            "description": "1000W 80+ Gold fully modular power supply.",
            "image": "https://source.unsplash.com/featured/?corsair,power+supply",
            "specs": {"wattage": "1000W", "efficiency": "80+ Gold", "modular": "Fully", "fan_size": "135mm"},
        },
        {
            "name": "Seasonic Prime TX-850",
            "brand": "Seasonic",
            "category": "PSU",
            "price": 249.99,
            "stock": 9,
            "description": "850W 80+ Titanium premium power supply.",
            "image": "https://source.unsplash.com/featured/?seasonic,psu",
            "specs": {"wattage": "850W", "efficiency": "80+ Titanium", "modular": "Fully", "fan_size": "135mm"},
        },
        # --- Cases ---
        {
            "name": "Lian Li O11 Dynamic EVO",
            "brand": "Lian Li",
            "category": "Case",
            "price": 169.99,
            "stock": 13,
            "description": "Versatile mid-tower case with dual-chamber design.",
            "image": "https://source.unsplash.com/featured/?lianli,pc+case",
            "specs": {"form_factor": "Mid-Tower", "material": "Aluminum/Glass", "max_gpu_length": "420mm", "fan_slots": 10},
        },
        {
            "name": "NZXT H7 Flow",
            "brand": "NZXT",
            "category": "Case",
            "price": 129.99,
            "stock": 16,
            "description": "High-airflow mid-tower ATX case.",
            "image": "https://source.unsplash.com/featured/?nzxt,case",
            "specs": {"form_factor": "Mid-Tower", "material": "Steel/Glass", "max_gpu_length": "400mm", "fan_slots": 9},
        },
        # --- Cooler ---
        {
            "name": "Noctua NH-D15 chromax.black",
            "brand": "Noctua",
            "category": "Cooler",
            "price": 109.99,
            "stock": 22,
            "description": "Dual-tower CPU air cooler, virtually silent.",
            "image": "https://source.unsplash.com/featured/?noctua,cooler",
            "specs": {"type": "Air", "fan_count": 2, "tdp_rating": "250W", "noise_level": "24.6 dBA"},
        },
        # --- Peripherals ---
        {
            "name": "Logitech G Pro X Superlight 2",
            "brand": "Logitech",
            "category": "Peripheral",
            "price": 159.99,
            "stock": 25,
            "description": "Ultra-lightweight wireless gaming mouse.",
            "image": "https://source.unsplash.com/featured/?logitech,mouse",
            "specs": {"type": "Mouse", "sensor": "HERO 2", "weight": "60g", "connectivity": "Wireless"},
        },
        {
            "name": "Corsair K100 RGB",
            "brand": "Corsair",
            "category": "Peripheral",
            "price": 229.99,
            "stock": 12,
            "description": "Premium mechanical gaming keyboard with OPX switches.",
            "image": "https://source.unsplash.com/featured/?corsair,keyboard",
            "specs": {"type": "Keyboard", "switches": "Corsair OPX", "layout": "Full-size", "connectivity": "Wired/Wireless"},
        },
    ]

    products_col.insert_many(products)

    # Create admin user if not exists
    if not users_col.find_one({"role": "admin"}):
        register_user("admin", "admin@electroswap.ch", "admin123")
        users_col.update_one({"username": "admin"}, {"$set": {"role": "admin"}})

    create_indexes()
    print(f"Seeded {len(products)} products and created indexes.")
