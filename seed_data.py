from datetime import datetime, timezone

SAMPLE_PRODUCTS = [
    {
        'name': 'Apple MacBook Pro 14"',
        'description': 'Powerful laptop with M3 Pro chip, 18GB RAM, 512GB SSD. Perfect for professionals.',
        'price': 1999.99,
        'category': 'Laptops',
        'brand': 'Apple',
        'sku': 'APPL-MBP14-M3PRO-512',
        'stock_quantity': 15,
        'condition': 'new',
        'weight': 1.6,
        'image_url': 'https://store.storeimages.cdn-apple.com/macbook-pro-14.jpg',
        'created_at': datetime(2024, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 1, 10, 9, 0, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Samsung Galaxy S24 Ultra',
        'description': '6.8" Dynamic AMOLED display, Snapdragon 8 Gen 3, 256GB storage, 200MP camera.',
        'price': 1299.99,
        'category': 'Smartphones',
        'brand': 'Samsung',
        'sku': 'SAMS-GS24U-256-BLK',
        'stock_quantity': 42,
        'condition': 'new',
        'weight': 0.232,
        'image_url': 'https://images.samsung.com/galaxy-s24-ultra.jpg',
        'created_at': datetime(2024, 2, 5, 11, 30, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 2, 5, 11, 30, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Sony WH-1000XM5 Headphones',
        'description': 'Industry-leading noise cancelling wireless headphones, 30-hour battery life.',
        'price': 349.99,
        'category': 'Audio',
        'brand': 'Sony',
        'sku': 'SONY-WH1000XM5-BLK',
        'stock_quantity': 78,
        'condition': 'new',
        'weight': 0.25,
        'image_url': 'https://www.sony.com/en/images/wh-1000xm5.jpg',
        'created_at': datetime(2024, 1, 20, 14, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 1, 20, 14, 0, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Apple iPad Pro 12.9" (used)',
        'description': 'Pre-owned iPad Pro with M2 chip, 256GB Wi-Fi + Cellular. Minor cosmetic wear.',
        'price': 799.00,
        'category': 'Tablets',
        'brand': 'Apple',
        'sku': 'APPL-IPADPRO129-M2-USED',
        'stock_quantity': 5,
        'condition': 'used',
        'weight': 0.682,
        'image_url': 'https://store.storeimages.cdn-apple.com/ipad-pro-12.jpg',
        'created_at': datetime(2024, 3, 1, 8, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 3, 1, 8, 0, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Dell XPS 15 Laptop',
        'description': 'Intel Core i7-13700H, RTX 4060, 32GB RAM, 1TB NVMe SSD, 15.6" OLED display.',
        'price': 1749.99,
        'category': 'Laptops',
        'brand': 'Dell',
        'sku': 'DELL-XPS15-i7-RTX4060',
        'stock_quantity': 9,
        'condition': 'new',
        'weight': 1.86,
        'image_url': 'https://i.dell.com/xps-15-9530.jpg',
        'created_at': datetime(2024, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Google Pixel 8 Pro',
        'description': 'Google Tensor G3 chip, 6.7" LTPO OLED, 50MP triple camera, 7 years of updates.',
        'price': 899.99,
        'category': 'Smartphones',
        'brand': 'Google',
        'sku': 'GOOG-PIX8PRO-128-OBS',
        'stock_quantity': 30,
        'condition': 'new',
        'weight': 0.213,
        'image_url': 'https://store.google.com/pixel-8-pro.jpg',
        'created_at': datetime(2024, 3, 10, 12, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 3, 10, 12, 0, 0, tzinfo=timezone.utc),
    },
    {
        'name': 'Bose QuietComfort 45',
        'description': 'Wireless noise cancelling headphones, up to 24 hours battery, foldable design.',
        'price': 249.99,
        'category': 'Audio',
        'brand': 'Bose',
        'sku': 'BOSE-QC45-WHT',
        'stock_quantity': 55,
        'condition': 'new',
        'weight': 0.238,
        'image_url': 'https://assets.bose.com/qc45-white.jpg',
        'created_at': datetime(2024, 1, 25, 16, 0, 0, tzinfo=timezone.utc),
        'updated_at': datetime(2024, 1, 25, 16, 0, 0, tzinfo=timezone.utc),
    },
]


def seed(db):
    if db.products.count_documents({}) == 0:
        db.products.insert_many([p.copy() for p in SAMPLE_PRODUCTS])
        print(f'Seeded {len(SAMPLE_PRODUCTS)} products.')
    else:
        print('Products collection already populated, skipping seed.')


if __name__ == '__main__':
    from app import create_app
    flask_app = create_app()
    with flask_app.app_context():
        mongo_db = flask_app.extensions['mongo_db']
        seed(mongo_db)
