"""Seed the MongoDB database with consistent Swiss demo data."""

import copy
import os
import random
from datetime import datetime, timedelta, timezone

import bcrypt
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/electroswap")
client = MongoClient(MONGO_URI)
db_name = MONGO_URI.rsplit("/", 1)[-1].split("?")[0]
db = client[db_name]

TARGET_COUNT = 1000
IMG = "https://placehold.co/600x400/1a1a2e/facc15?text="


def to_chf(price_usd):
    """Convert a USD-like seed value to Swiss francs (CHF)."""
    return round(price_usd * 0.92, 2)


def build_products(now):
    """Create at least TARGET_COUNT products with CHF prices."""
    base_products = [
        {
            "name": "AMD Ryzen 9 7950X",
            "brand": "AMD",
            "price": to_chf(549.00),
            "category": "CPU",
            "stock_quantity": 45,
            "images": [IMG + "Ryzen+9+7950X"],
            "description": "16-core, 32-thread unlocked desktop processor with Zen 4 architecture.",
            "specs": {"cores": 16, "threads": 32, "socket": "AM5", "base_clock": "4.5 GHz", "boost_clock": "5.7 GHz", "tdp": 170, "cache": "80 MB"},
            "created_at": now,
        },
        {
            "name": "Intel Core i9-14900K",
            "brand": "Intel",
            "price": to_chf(589.00),
            "category": "CPU",
            "stock_quantity": 40,
            "images": [IMG + "i9-14900K"],
            "description": "24-core (8P+16E) desktop processor with up to 6.0 GHz turbo.",
            "specs": {"cores": 24, "threads": 32, "socket": "LGA 1700", "base_clock": "3.2 GHz", "boost_clock": "6.0 GHz", "tdp": 253, "cache": "36 MB"},
            "created_at": now,
        },
        {
            "name": "AMD Ryzen 7 7800X3D",
            "brand": "AMD",
            "price": to_chf(399.00),
            "category": "CPU",
            "stock_quantity": 55,
            "images": [IMG + "Ryzen+7+7800X3D"],
            "description": "8-core gaming processor with 3D V-Cache technology.",
            "specs": {"cores": 8, "threads": 16, "socket": "AM5", "base_clock": "4.2 GHz", "boost_clock": "5.0 GHz", "tdp": 120, "cache": "104 MB"},
            "created_at": now,
        },
        {
            "name": "NVIDIA GeForce RTX 4090",
            "brand": "NVIDIA",
            "price": to_chf(1799.00),
            "category": "GPU",
            "stock_quantity": 30,
            "images": [IMG + "RTX+4090"],
            "description": "The ultimate GPU for gamers and creators, powered by Ada Lovelace.",
            "specs": {"chipset": "AD102", "memory": "24 GB GDDR6X", "boost_clock": "2520 MHz", "cuda_cores": 16384, "tdp": 450, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        {
            "name": "AMD Radeon RX 7900 XTX",
            "brand": "AMD",
            "price": to_chf(949.00),
            "category": "GPU",
            "stock_quantity": 35,
            "images": [IMG + "RX+7900+XTX"],
            "description": "Flagship RDNA 3 graphics card with 24 GB memory.",
            "specs": {"chipset": "Navi 31", "memory": "24 GB GDDR6", "boost_clock": "2500 MHz", "stream_processors": 6144, "tdp": 355, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        {
            "name": "NVIDIA GeForce RTX 4070 Ti Super",
            "brand": "NVIDIA",
            "price": to_chf(799.00),
            "category": "GPU",
            "stock_quantity": 50,
            "images": [IMG + "RTX+4070+Ti"],
            "description": "High-performance gaming GPU with DLSS 3 and ray tracing.",
            "specs": {"chipset": "AD103", "memory": "16 GB GDDR6X", "boost_clock": "2610 MHz", "cuda_cores": 8448, "tdp": 285, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        {
            "name": "Samsung Odyssey G9 49\"",
            "brand": "Samsung",
            "price": to_chf(1299.00),
            "category": "Monitor",
            "stock_quantity": 25,
            "images": [IMG + "Odyssey+G9"],
            "description": "49-inch super ultra-wide curved gaming monitor.",
            "specs": {"panel": "VA", "resolution": "5120x1440", "refresh_rate": "240 Hz", "response_time": "1 ms", "hdr": "HDR1000", "curve": "1000R"},
            "created_at": now,
        },
        {
            "name": "LG UltraGear 27GP950-B",
            "brand": "LG",
            "price": to_chf(699.00),
            "category": "Monitor",
            "stock_quantity": 40,
            "images": [IMG + "LG+27GP950"],
            "description": "27-inch 4K Nano IPS gaming monitor with HDMI 2.1.",
            "specs": {"panel": "Nano IPS", "resolution": "3840x2160", "refresh_rate": "160 Hz", "response_time": "1 ms", "hdr": "HDR600", "size": "27 inch"},
            "created_at": now,
        },
        {
            "name": "ASUS ROG Crosshair X670E Hero",
            "brand": "ASUS",
            "price": to_chf(699.00),
            "category": "Motherboard",
            "stock_quantity": 45,
            "images": [IMG + "X670E+Hero"],
            "description": "Premium AM5 motherboard with DDR5 and PCIe 5.0 support.",
            "specs": {"socket": "AM5", "chipset": "X670E", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5", "pcie_slots": "2x PCIe 5.0 x16", "m2_slots": 4},
            "created_at": now,
        },
        {
            "name": "MSI MAG Z790 Tomahawk",
            "brand": "MSI",
            "price": to_chf(289.00),
            "category": "Motherboard",
            "stock_quantity": 55,
            "images": [IMG + "Z790+Tomahawk"],
            "description": "Solid LGA 1700 motherboard for Intel 13th/14th gen.",
            "specs": {"socket": "LGA 1700", "chipset": "Z790", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5", "pcie_slots": "1x PCIe 5.0 x16", "m2_slots": 4},
            "created_at": now,
        },
        {
            "name": "G.Skill Trident Z5 RGB 32GB DDR5-6000",
            "brand": "G.Skill",
            "price": to_chf(129.00),
            "category": "RAM",
            "stock_quantity": 80,
            "images": [IMG + "Trident+Z5"],
            "description": "High-speed DDR5 memory kit optimized for AMD EXPO.",
            "specs": {"capacity": "32 GB (2x16 GB)", "type": "DDR5", "speed": "6000 MHz", "latency": "CL30", "voltage": "1.35V", "rgb": True},
            "created_at": now,
        },
        {
            "name": "Corsair Vengeance DDR5-5600 64GB",
            "brand": "Corsair",
            "price": to_chf(189.00),
            "category": "RAM",
            "stock_quantity": 70,
            "images": [IMG + "Vengeance+DDR5"],
            "description": "64 GB DDR5 kit for content creation and multitasking.",
            "specs": {"capacity": "64 GB (2x32 GB)", "type": "DDR5", "speed": "5600 MHz", "latency": "CL36", "voltage": "1.25V", "rgb": False},
            "created_at": now,
        },
        {
            "name": "Corsair RM1000x",
            "brand": "Corsair",
            "price": to_chf(189.00),
            "category": "PSU",
            "stock_quantity": 50,
            "images": [IMG + "RM1000x"],
            "description": "1000W fully modular ATX 3.0 power supply, 80+ Gold.",
            "specs": {"wattage": 1000, "efficiency": "80+ Gold", "modular": "Fully Modular", "fan_size": "135 mm", "atx_version": "ATX 3.0", "connector_12vhpwr": True},
            "created_at": now,
        },
        {
            "name": "Samsung 990 Pro 2TB NVMe",
            "brand": "Samsung",
            "price": to_chf(179.00),
            "category": "Storage",
            "stock_quantity": 90,
            "images": [IMG + "990+Pro"],
            "description": "Ultra-fast PCIe 4.0 NVMe SSD with sequential reads up to 7450 MB/s.",
            "specs": {"capacity": "2 TB", "interface": "PCIe 4.0 x4 NVMe", "seq_read": "7450 MB/s", "seq_write": "6900 MB/s", "form_factor": "M.2 2280", "endurance": "1200 TBW"},
            "created_at": now,
        },
        {
            "name": "WD Black SN850X 1TB",
            "brand": "Western Digital",
            "price": to_chf(89.00),
            "category": "Storage",
            "stock_quantity": 100,
            "images": [IMG + "SN850X"],
            "description": "High-performance gaming SSD with heatsink option.",
            "specs": {"capacity": "1 TB", "interface": "PCIe 4.0 x4 NVMe", "seq_read": "7300 MB/s", "seq_write": "6300 MB/s", "form_factor": "M.2 2280", "endurance": "600 TBW"},
            "created_at": now,
        },
        {
            "name": "Lian Li O11 Dynamic EVO",
            "brand": "Lian Li",
            "price": to_chf(169.00),
            "category": "Case",
            "stock_quantity": 60,
            "images": [IMG + "O11+Dynamic"],
            "description": "Premium dual-chamber mid-tower case with exceptional airflow.",
            "specs": {"form_factor": "Mid-Tower", "motherboard_support": "E-ATX/ATX/mATX/ITX", "max_gpu_length": "422 mm", "drive_bays": "4x 2.5\" / 2x 3.5\"", "fans_included": 0, "max_fans": 10},
            "created_at": now,
        },
        {
            "name": "Noctua NH-D15 chromax.black",
            "brand": "Noctua",
            "price": to_chf(109.00),
            "category": "Cooling",
            "stock_quantity": 75,
            "images": [IMG + "Noctua+NH-D15"],
            "description": "Premium dual-tower CPU cooler with excellent thermals and low noise.",
            "specs": {"type": "Air Cooler", "height": "165 mm", "fans": 2, "socket_support": "AM4/AM5/LGA1700"},
            "created_at": now,
        },
        {
            "name": "Corsair iCUE H150i ELITE CAPELLIX XT",
            "brand": "Corsair",
            "price": to_chf(179.00),
            "category": "Cooling",
            "stock_quantity": 55,
            "images": [IMG + "Corsair+H150i"],
            "description": "360mm AIO liquid cooler with high-performance RGB pump and fans.",
            "specs": {"type": "AIO", "radiator": "360 mm", "fans": 3, "rgb": True},
            "created_at": now,
        },
        {
            "name": "Logitech G Pro X Superlight 2",
            "brand": "Logitech",
            "price": to_chf(139.00),
            "category": "Peripherals",
            "stock_quantity": 120,
            "images": [IMG + "GPX+Superlight+2"],
            "description": "Ultra-light wireless esports mouse with HERO sensor and long battery life.",
            "specs": {"weight": "~60g", "connection": "Wireless", "sensor": "HERO", "dpi": "Up to 32k"},
            "created_at": now,
        },
        {
            "name": "Keychron Q1 Pro",
            "brand": "Keychron",
            "price": to_chf(199.00),
            "category": "Peripherals",
            "stock_quantity": 65,
            "images": [IMG + "Keychron+Q1+Pro"],
            "description": "Premium QMK/VIA mechanical keyboard with wireless support and aluminum body.",
            "specs": {"layout": "75%", "connection": "Wireless/USB-C", "switches": "Hot-swappable", "case": "Aluminum"},
            "created_at": now,
        },
        {
            "name": "ASUS ROG Strix XG27AQ",
            "brand": "ASUS",
            "price": to_chf(449.00),
            "category": "Monitor",
            "stock_quantity": 50,
            "images": [IMG + "ROG+XG27AQ"],
            "description": "27-inch 1440p IPS monitor with 170 Hz refresh rate for smooth gaming.",
            "specs": {"panel": "IPS", "resolution": "2560x1440", "refresh_rate": "170 Hz", "response_time": "1 ms"},
            "created_at": now,
        },
    ]

    variant_index = 1
    while len(base_products) < TARGET_COUNT:
        source = copy.deepcopy(base_products[(variant_index - 1) % len(base_products)])
        source["name"] = f"{source['name']} Edition {variant_index}"
        source["price"] = round(source["price"] * (1 + (variant_index % 4) * 0.03), 2)
        source["stock_quantity"] += 10 + variant_index
        source["images"] = [source["images"][0] + f"+E{variant_index}"]
        source["created_at"] = now - timedelta(days=variant_index)
        base_products.append(source)
        variant_index += 1

    return base_products


def seed():
    """Drop existing data and insert fresh seed data."""
    random.seed(42)
    now = datetime.now(timezone.utc)

    for col in ["users", "products", "baskets", "wishlists", "orders", "reviews"]:
        db[col].drop()

    admin_pw_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    customer_pw_hash = bcrypt.hashpw(b"customer123", bcrypt.gensalt()).decode()

    db.users.insert_one({
        "username": "admin",
        "email": "admin@electroswap.ch",
        "password_hash": admin_pw_hash,
        "role": "admin",
        "address": {"street": "Bahnhofstr. 1", "city": "Zurich", "zip_code": "8001", "country": "Switzerland"},
        "created_at": now,
    })

    first_names = [
        "luca", "mia", "noah", "sara", "liam", "emma", "elias", "nina", "jonas", "lea",
        "leo", "sofia", "gabriel", "chloe", "david", "laura", "matteo", "alina",
        "elena", "samuel", "daniel", "julia", "martin", "anna", "ben", "lara",
        "simon", "valentina", "rafael", "chiara", "robin", "fabian", "melina", "janis"
    ]
    cities = [
        "Zurich", "Bern", "Basel", "Geneva", "Lausanne", "Lucerne", "St. Gallen",
        "Lugano", "Winterthur", "Biel/Bienne", "Thun", "Fribourg", "Schaffhausen",
        "Chur", "Neuchâtel", "Sion", "Zug", "Aarau", "Olten", "Solothurn"
    ]

    customer_docs = [
        {
            "username": "demo_customer",
            "email": "customer@electroswap.ch",
            "password_hash": customer_pw_hash,
            "role": "customer",
            "address": {"street": "Hauptstr. 10", "city": "Bern", "zip_code": "3011", "country": "Switzerland"},
            "created_at": now,
        }
    ]

    while len(customer_docs) < TARGET_COUNT:
        idx = len(customer_docs)
        name = first_names[idx % len(first_names)]
        city = cities[idx % len(cities)]
        username = f"{name}{idx:02d}"
        customer_docs.append({
            "username": username,
            "email": f"{username}@electroswap.ch",
            "password_hash": customer_pw_hash,
            "role": "customer",
            "address": {
                "street": f"Musterweg {100 + idx}",
                "city": city,
                "zip_code": f"{8000 + idx}",
                "country": "Switzerland",
            },
            "created_at": now - timedelta(days=idx),
        })

    user_insert_result = db.users.insert_many(customer_docs)
    customer_ids = user_insert_result.inserted_ids

    products = build_products(now)
    product_ids = db.products.insert_many(products).inserted_ids

    baskets = []
    for i in range(TARGET_COUNT):
        uid = customer_ids[i]
        item_count = 2 + (i % 2)
        items = []
        for j in range(item_count):
            pid = product_ids[(i * 3 + j) % len(product_ids)]
            items.append({"product_id": pid, "quantity": 1 + ((i + j) % 3)})
        baskets.append({
            "user_id": uid,
            "items": items,
            "last_updated": now - timedelta(hours=i),
        })
    db.baskets.insert_many(baskets)

    wishlists = []
    for i in range(TARGET_COUNT):
        uid = customer_ids[i]
        item_count = 2 + (i % 3)
        items = []
        for j in range(item_count):
            pid = product_ids[(i * 2 + j + 5) % len(product_ids)]
            items.append({
                "product_id": pid,
                "added_at": now - timedelta(days=i, minutes=j * 10),
            })
        wishlists.append({
            "user_id": uid,
            "name": f"Wishlist {i + 1}",
            "items": items,
        })
    db.wishlists.insert_many(wishlists)

    orders = []
    for i in range(TARGET_COUNT):
        uid = customer_ids[i]
        item_count = 1 + (i % 3)
        order_items = []
        total_price = 0
        for j in range(item_count):
            product_doc = products[(i + j * 4) % len(products)]
            qty = 1 + ((i + j) % 2)
            line_price = product_doc["price"] * qty
            total_price += line_price
            order_items.append({
                "product_id": product_ids[(i + j * 4) % len(product_ids)],
                "name_at_purchase": product_doc["name"],
                "price_at_purchase": product_doc["price"],
                "quantity": qty,
            })

        user_doc = customer_docs[i]
        orders.append({
            "user_id": uid,
            "order_date": now - timedelta(days=i),
            "total_price": round(total_price, 2),
            "status": "confirmed",
            "shipping_address": user_doc["address"],
            "order_items": order_items,
        })
    db.orders.insert_many(orders)

    review_texts = [
        (5, "Excellent build quality and performance. Exactly as described."),
        (4, "Great value. Shipping was fast and packaging was solid."),
        (5, "Perfect for my build. Temps and stability are great."),
        (3, "Works fine, but I expected slightly better acoustics."),
        (4, "Good product overall. Would buy again."),
        (5, "Top quality and fast delivery inside Switzerland."),
    ]

    reviews = []
    for i in range(TARGET_COUNT):
        rating, comment = review_texts[i % len(review_texts)]
        reviews.append({
            "product_id": product_ids[i % len(product_ids)],
            "user_id": customer_ids[(i * 3) % len(customer_ids)],
            "rating": rating,
            "comment": comment,
            "created_at": now - timedelta(days=i, hours=i % 7),
        })
    db.reviews.insert_many(reviews)

    print("✓ Seed complete")
    print(f"  users: {db.users.count_documents({})}")
    print(f"  products: {db.products.count_documents({})}")
    print(f"  baskets: {db.baskets.count_documents({})}")
    print(f"  wishlists: {db.wishlists.count_documents({})}")
    print(f"  orders: {db.orders.count_documents({})}")
    print(f"  reviews: {db.reviews.count_documents({})}")
    print("✓ Login admin  → admin@electroswap.ch / admin123")
    print("✓ Login customer → customer@electroswap.ch / customer123")


if __name__ == "__main__":
    seed()
    print("\nDone! 🚀")
