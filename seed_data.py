"""Seed the MongoDB database with sample products and an admin user."""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
import bcrypt

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/electroswap")
client = MongoClient(MONGO_URI)
db_name = MONGO_URI.rsplit("/", 1)[-1].split("?")[0]
db = client[db_name]

# ── Helper ──────────────────────────────────────────────
now = datetime.now(timezone.utc)
IMG = "https://placehold.co/600x400/1a1a2e/facc15?text="


def seed():
    """Drop existing data and insert fresh seed data."""
    for col in ["users", "products", "baskets", "wishlists", "orders", "reviews"]:
        db[col].drop()

    # ── Admin user ──────────────────────────────────────
    admin_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    db.users.insert_one({
        "username": "admin",
        "email": "admin@electroswap.ch",
        "password_hash": admin_pw,
        "role": "admin",
        "address": {"street": "Bahnhofstr. 1", "city": "Zurich", "zip_code": "8001", "country": "Switzerland"},
        "created_at": now,
    })

    # ── Demo customer ────────────────────────────────────
    cust_pw = bcrypt.hashpw(b"customer123", bcrypt.gensalt()).decode()
    db.users.insert_one({
        "username": "demo_customer",
        "email": "customer@electroswap.ch",
        "password_hash": cust_pw,
        "role": "customer",
        "address": {"street": "Hauptstr. 10", "city": "Bern", "zip_code": "3011", "country": "Switzerland"},
        "created_at": now,
    })

    # ── Products ────────────────────────────────────────
    products = [
        # CPUs
        {
            "name": "AMD Ryzen 9 7950X",
            "brand": "AMD",
            "price": 549.00,
            "category": "CPU",
            "stock_quantity": 25,
            "images": [IMG + "Ryzen+9+7950X"],
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
            "images": [IMG + "i9-14900K"],
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
            "images": [IMG + "Ryzen+7+7800X3D"],
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
            "images": [IMG + "RTX+4090"],
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
            "images": [IMG + "RX+7900+XTX"],
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
            "images": [IMG + "RTX+4070+Ti"],
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
            "images": [IMG + "Odyssey+G9"],
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
            "images": [IMG + "LG+27GP950"],
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
            "images": [IMG + "X670E+Hero"],
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
            "images": [IMG + "Z790+Tomahawk"],
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
            "images": [IMG + "Trident+Z5"],
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
            "images": [IMG + "Vengeance+DDR5"],
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
            "images": [IMG + "RM1000x"],
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
            "images": [IMG + "990+Pro"],
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
            "images": [IMG + "SN850X"],
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
            "images": [IMG + "O11+Dynamic"],
            "description": "Premium dual-chamber mid-tower case with exceptional airflow.",
            "specs": {"form_factor": "Mid-Tower", "motherboard_support": "E-ATX/ATX/mATX/ITX", "max_gpu_length": "422 mm", "drive_bays": "4x 2.5\" / 2x 3.5\"", "fans_included": 0, "max_fans": 10},
            "created_at": now,
        },
    ]

    db.products.insert_many(products)
    print(f"✓ Seeded {len(products)} products")
    print("✓ Created admin user  → admin@electroswap.ch / admin123")
    print("✓ Created demo customer → customer@electroswap.ch / customer123")


if __name__ == "__main__":
    seed()
    print("\nDone! 🚀")
