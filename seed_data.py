"""Seed the MongoDB database with sample products and an admin user."""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
import bcrypt

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/electroswap")
client = MongoClient(MONGO_URI)
db_name = MONGO_URI.rsplit("/", 1)[-1].split("?")[0]
db = client[db_name]

# -- Helper -------------------------------------------------------
now = datetime.now(timezone.utc)
# Local product image path prefix (served via Flask static)
IMG_DIR = "/static/images/products/"


def seed():
    """Drop existing data and insert fresh seed data."""
    for col in ["users", "products", "baskets", "wishlists", "orders", "reviews"]:
        db[col].drop()

    # -- Admin user --------------------------------------------
    admin_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    admin_id = db.users.insert_one({
        "username": "admin",
        "email": "admin@electroswap.ch",
        "password_hash": admin_pw,
        "role": "admin",
        "address": {"street": "Bahnhofstr. 1", "city": "Zurich", "zip_code": "8001", "country": "Switzerland"},
        "created_at": now,
    }).inserted_id

    # -- Demo customer ------------------------------------------
    cust_pw = bcrypt.hashpw(b"customer123", bcrypt.gensalt()).decode()
    customer_id = db.users.insert_one({
        "username": "demo_customer",
        "email": "customer@electroswap.ch",
        "password_hash": cust_pw,
        "role": "customer",
        "address": {"street": "Hauptstr. 10", "city": "Bern", "zip_code": "3011", "country": "Switzerland"},
        "created_at": now,
    }).inserted_id

    # -- Additional demo users (realistic Live-Demo) ---------------
    demo_users = [
        ("luca", "luca@electroswap.ch", "Zurich"),
        ("mia", "mia@electroswap.ch", "Basel"),
        ("noah", "noah@electroswap.ch", "Geneva"),
        ("sara", "sara@electroswap.ch", "Lausanne"),
    ]
    demo_user_ids = []
    for username, email, city in demo_users:
        pw = bcrypt.hashpw(b"customer123", bcrypt.gensalt()).decode()
        demo_user_ids.append(
            db.users.insert_one({
                "username": username,
                "email": email,
                "password_hash": pw,
                "role": "customer",
                "address": {"street": "Demo Street 1", "city": city, "zip_code": "8000", "country": "Switzerland"},
                "created_at": now,
            }).inserted_id
        )

    # -- Products ------------------------------------------------
    products = [
        # CPUs
        {
            "name": "AMD Ryzen 9 7950X",
            "brand": "AMD",
            "price": 549.00,
            "category": "CPU",
            "stock_quantity": 25,
            "images": [IMG_DIR + "ryzen-9-7950x.jpg"],
            "description": "16-core, 32-thread unlocked desktop processor with Zen 4 architecture.",
            "specs": {"cores": 16, "threads": 32, "socket": "AM5", "base_clock": "4.5 GHz", "boost_clock": "5.7 GHz", "tdp": 170, "cache": "80 MB"},
            "created_at": now,
        },
        {
            "name": "Intel Core i9-14900K",
            "brand": "Intel",
            "price": 589.00,
            "category": "CPU",
            "stock_quantity": 18,
            "images": [IMG_DIR + "i9-14900k.jpg"],
            "description": "24-core (8P+16E) desktop processor with up to 6.0 GHz turbo.",
            "specs": {"cores": 24, "threads": 32, "socket": "LGA 1700", "base_clock": "3.2 GHz", "boost_clock": "6.0 GHz", "tdp": 253, "cache": "36 MB"},
            "created_at": now,
        },
        {
            "name": "AMD Ryzen 7 7800X3D",
            "brand": "AMD",
            "price": 399.00,
            "category": "CPU",
            "stock_quantity": 30,
            "images": [IMG_DIR + "ryzen-7-7800x3d.jpg"],
            "description": "8-core gaming processor with 3D V-Cache technology.",
            "specs": {"cores": 8, "threads": 16, "socket": "AM5", "base_clock": "4.2 GHz", "boost_clock": "5.0 GHz", "tdp": 120, "cache": "104 MB"},
            "created_at": now,
        },
        # GPUs
        {
            "name": "NVIDIA GeForce RTX 4090",
            "brand": "NVIDIA",
            "price": 1799.00,
            "category": "GPU",
            "stock_quantity": 10,
            "images": [IMG_DIR + "rtx-4090.jpg"],
            "description": "The ultimate GPU for gamers and creators, powered by Ada Lovelace.",
            "specs": {"chipset": "AD102", "memory": "24 GB GDDR6X", "boost_clock": "2520 MHz", "cuda_cores": 16384, "tdp": 450, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        {
            "name": "AMD Radeon RX 7900 XTX",
            "brand": "AMD",
            "price": 949.00,
            "category": "GPU",
            "stock_quantity": 15,
            "images": [IMG_DIR + "rx-7900-xtx.jpg"],
            "description": "Flagship RDNA 3 graphics card with 24 GB memory.",
            "specs": {"chipset": "Navi 31", "memory": "24 GB GDDR6", "boost_clock": "2500 MHz", "stream_processors": 6144, "tdp": 355, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        {
            "name": "NVIDIA GeForce RTX 4070 Ti Super",
            "brand": "NVIDIA",
            "price": 799.00,
            "category": "GPU",
            "stock_quantity": 20,
            "images": [IMG_DIR + "rtx-4070-ti.jpg"],
            "description": "High-performance gaming GPU with DLSS 3 and ray tracing.",
            "specs": {"chipset": "AD103", "memory": "16 GB GDDR6X", "boost_clock": "2610 MHz", "cuda_cores": 8448, "tdp": 285, "interface": "PCIe 4.0 x16"},
            "created_at": now,
        },
        # Monitors
        {
            "name": "Samsung Odyssey G9 49\"",
            "brand": "Samsung",
            "price": 1299.00,
            "category": "Monitor",
            "stock_quantity": 8,
            "images": [IMG_DIR + "odyssey-g9.jpg"],
            "description": "49-inch super ultra-wide curved gaming monitor.",
            "specs": {"panel": "VA", "resolution": "5120x1440", "refresh_rate": "240 Hz", "response_time": "1 ms", "hdr": "HDR1000", "curve": "1000R"},
            "created_at": now,
        },
        {
            "name": "LG UltraGear 27GP950-B",
            "brand": "LG",
            "price": 699.00,
            "category": "Monitor",
            "stock_quantity": 12,
            "images": [IMG_DIR + "lg-27gp950.jpg"],
            "description": "27-inch 4K Nano IPS gaming monitor with HDMI 2.1.",
            "specs": {"panel": "Nano IPS", "resolution": "3840x2160", "refresh_rate": "160 Hz", "response_time": "1 ms", "hdr": "HDR600", "size": "27 inch"},
            "created_at": now,
        },
        # Motherboards
        {
            "name": "ASUS ROG Crosshair X670E Hero",
            "brand": "ASUS",
            "price": 699.00,
            "category": "Motherboard",
            "stock_quantity": 14,
            "images": [IMG_DIR + "x670e-hero.jpg"],
            "description": "Premium AM5 motherboard with DDR5 and PCIe 5.0 support.",
            "specs": {"socket": "AM5", "chipset": "X670E", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5", "pcie_slots": "2x PCIe 5.0 x16", "m2_slots": 4},
            "created_at": now,
        },
        {
            "name": "MSI MAG Z790 Tomahawk",
            "brand": "MSI",
            "price": 289.00,
            "category": "Motherboard",
            "stock_quantity": 22,
            "images": [IMG_DIR + "z790-tomahawk.jpg"],
            "description": "Solid LGA 1700 motherboard for Intel 13th/14th gen.",
            "specs": {"socket": "LGA 1700", "chipset": "Z790", "form_factor": "ATX", "ram_slots": 4, "max_ram": "128 GB DDR5", "pcie_slots": "1x PCIe 5.0 x16", "m2_slots": 4},
            "created_at": now,
        },
        # RAM
        {
            "name": "G.Skill Trident Z5 RGB 32GB DDR5-6000",
            "brand": "G.Skill",
            "price": 129.00,
            "category": "RAM",
            "stock_quantity": 50,
            "images": [IMG_DIR + "trident-z5.jpg"],
            "description": "High-speed DDR5 memory kit optimized for AMD EXPO.",
            "specs": {"capacity": "32 GB (2x16 GB)", "type": "DDR5", "speed": "6000 MHz", "latency": "CL30", "voltage": "1.35V", "rgb": True},
            "created_at": now,
        },
        {
            "name": "Corsair Vengeance DDR5-5600 64GB",
            "brand": "Corsair",
            "price": 189.00,
            "category": "RAM",
            "stock_quantity": 35,
            "images": [IMG_DIR + "vengeance-ddr5.jpg"],
            "description": "64 GB DDR5 kit for content creation and multitasking.",
            "specs": {"capacity": "64 GB (2x32 GB)", "type": "DDR5", "speed": "5600 MHz", "latency": "CL36", "voltage": "1.25V", "rgb": False},
            "created_at": now,
        },
        # PSU
        {
            "name": "Corsair RM1000x",
            "brand": "Corsair",
            "price": 189.00,
            "category": "PSU",
            "stock_quantity": 20,
            "images": [IMG_DIR + "rm1000x.jpg"],
            "description": "1000W fully modular ATX 3.0 power supply, 80+ Gold.",
            "specs": {"wattage": 1000, "efficiency": "80+ Gold", "modular": "Fully Modular", "fan_size": "135 mm", "atx_version": "ATX 3.0", "connector_12vhpwr": True},
            "created_at": now,
        },
        # Storage
        {
            "name": "Samsung 990 Pro 2TB NVMe",
            "brand": "Samsung",
            "price": 179.00,
            "category": "Storage",
            "stock_quantity": 40,
            "images": [IMG_DIR + "990-pro.jpg"],
            "description": "Ultra-fast PCIe 4.0 NVMe SSD with sequential reads up to 7450 MB/s.",
            "specs": {"capacity": "2 TB", "interface": "PCIe 4.0 x4 NVMe", "seq_read": "7450 MB/s", "seq_write": "6900 MB/s", "form_factor": "M.2 2280", "endurance": "1200 TBW"},
            "created_at": now,
        },
        {
            "name": "WD Black SN850X 1TB",
            "brand": "Western Digital",
            "price": 89.00,
            "category": "Storage",
            "stock_quantity": 45,
            "images": [IMG_DIR + "sn850x.jpg"],
            "description": "High-performance gaming SSD with heatsink option.",
            "specs": {"capacity": "1 TB", "interface": "PCIe 4.0 x4 NVMe", "seq_read": "7300 MB/s", "seq_write": "6300 MB/s", "form_factor": "M.2 2280", "endurance": "600 TBW"},
            "created_at": now,
        },
        # Case
        {
            "name": "Lian Li O11 Dynamic EVO",
            "brand": "Lian Li",
            "price": 169.00,
            "category": "Case",
            "stock_quantity": 18,
            "images": [IMG_DIR + "o11-dynamic.jpg"],
            "description": "Premium dual-chamber mid-tower case with exceptional airflow.",
            "specs": {"form_factor": "Mid-Tower", "motherboard_support": "E-ATX/ATX/mATX/ITX", "max_gpu_length": "422 mm", "drive_bays": "4x 2.5\" / 2x 3.5\"", "fans_included": 0, "max_fans": 10},
            "created_at": now,
        },
    ]

    # Add more products to ensure >= 20 (criterion 2.9)
    extra_products = [
        {
            "name": "Noctua NH-D15 chromax.black",
            "brand": "Noctua",
            "price": 109.00,
            "category": "Cooling",
            "stock_quantity": 28,
            "images": [IMG_DIR + "noctua-nh-d15.jpg"],
            "description": "Premium dual-tower CPU cooler with excellent thermals and low noise.",
            "specs": {"type": "Air Cooler", "height": "165 mm", "fans": 2, "socket_support": "AM4/AM5/LGA1700"},
            "created_at": now,
        },
        {
            "name": "Corsair iCUE H150i ELITE CAPELLIX XT",
            "brand": "Corsair",
            "price": 179.00,
            "category": "Cooling",
            "stock_quantity": 16,
            "images": [IMG_DIR + "corsair-h150i.jpg"],
            "description": "360mm AIO liquid cooler with high-performance RGB pump and fans.",
            "specs": {"type": "AIO", "radiator": "360 mm", "fans": 3, "rgb": True},
            "created_at": now,
        },
        {
            "name": "Logitech G Pro X Superlight 2",
            "brand": "Logitech",
            "price": 139.00,
            "category": "Peripherals",
            "stock_quantity": 60,
            "images": [IMG_DIR + "gpx-superlight-2.jpg"],
            "description": "Ultra-light wireless esports mouse with HERO sensor and long battery life.",
            "specs": {"weight": "~60g", "connection": "Wireless", "sensor": "HERO", "dpi": "Up to 32k"},
            "created_at": now,
        },
        {
            "name": "Keychron Q1 Pro",
            "brand": "Keychron",
            "price": 199.00,
            "category": "Peripherals",
            "stock_quantity": 22,
            "images": [IMG_DIR + "keychron-q1-pro.jpg"],
            "description": "Premium QMK/VIA mechanical keyboard with wireless support and aluminum body.",
            "specs": {"layout": "75%", "connection": "Wireless/USB-C", "switches": "Hot-swappable", "case": "Aluminum"},
            "created_at": now,
        },
        {
            "name": "ASUS ROG Strix XG27AQ",
            "brand": "ASUS",
            "price": 449.00,
            "category": "Monitor",
            "stock_quantity": 19,
            "images": [IMG_DIR + "rog-xg27aq.jpg"],
            "description": "27-inch 1440p IPS monitor with 170 Hz refresh rate for smooth gaming.",
            "specs": {"panel": "IPS", "resolution": "2560x1440", "refresh_rate": "170 Hz", "response_time": "1 ms"},
            "created_at": now,
        },
    ]

    products.extend(extra_products)

    inserted_ids = db.products.insert_many(products).inserted_ids
    print(f"  Seeded {len(products)} products")

    # -- Seed realistic reviews (>= 20) ---------------------------
    # Attach reviews to some products for Live-Demo.
    review_texts = [
        (5, "Excellent build quality and performance. Exactly as described."),
        (4, "Great value. Shipping was fast and packaging was solid."),
        (5, "Perfect for my new build. Temps and stability are great."),
        (3, "Works fine, but I expected slightly better acoustics."),
        (4, "Good product overall. Would buy again."),
    ]

    review_docs = []
    # create 20 reviews across first 10 products
    for i in range(20):
        product_id = inserted_ids[i % min(10, len(inserted_ids))]
        user_id = demo_user_ids[i % len(demo_user_ids)] if demo_user_ids else customer_id
        rating, comment = review_texts[i % len(review_texts)]
        review_docs.append({
            "product_id": product_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "created_at": now,
        })

    if review_docs:
        db.reviews.insert_many(review_docs)
        print(f"  Seeded {len(review_docs)} reviews")

    print("  Created admin user  -> admin@electroswap.ch / admin123")
    print("  Created demo customer -> customer@electroswap.ch / customer123")
    print("  Created extra demo users -> (all with password) customer123")


if __name__ == "__main__":
    seed()
    print("\nDone. Database seeded successfully.")
