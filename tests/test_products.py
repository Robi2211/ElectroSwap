import unittest
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mongomock
from datetime import datetime, timezone
from app.models.product import Product
from seed_data import SAMPLE_PRODUCTS


VALID_PRODUCT_DATA = {
    'name': 'Test Laptop',
    'description': 'A high-performance test laptop for unit testing.',
    'price': 999.99,
    'category': 'Laptops',
    'brand': 'TestBrand',
    'sku': 'TEST-LAP-001',
    'stock_quantity': 10,
    'condition': 'new',
    'weight': 1.5,
    'image_url': 'https://example.com/laptop.jpg',
    'created_at': datetime(2024, 1, 1, tzinfo=timezone.utc),
    'updated_at': datetime(2024, 1, 1, tzinfo=timezone.utc),
}


class TestProductFields(unittest.TestCase):

    def test_product_has_all_12_fields(self):
        expected = {
            'name', 'description', 'price', 'category', 'brand',
            'sku', 'stock_quantity', 'condition', 'weight', 'image_url',
            'created_at', 'updated_at',
        }
        self.assertEqual(set(Product.FIELDS), expected)

    def test_fields_length_at_least_8(self):
        self.assertGreaterEqual(len(Product.FIELDS), 8)

    def test_required_fields_length_at_least_8(self):
        self.assertGreaterEqual(len(Product.REQUIRED_FIELDS), 8)

    def test_mandatory_fields_in_required(self):
        mandatory = ['name', 'description', 'price', 'category', 'brand',
                     'sku', 'stock_quantity', 'condition']
        for field in mandatory:
            self.assertIn(field, Product.REQUIRED_FIELDS,
                          f"'{field}' should be in REQUIRED_FIELDS")


class TestProductFromDictToDict(unittest.TestCase):

    def test_from_dict_creates_product(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        self.assertIsInstance(product, Product)

    def test_from_dict_sets_all_fields(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        d = product.to_dict()
        for field in Product.FIELDS:
            self.assertIn(field, d, f"Field '{field}' missing from to_dict() result")

    def test_from_dict_preserves_values(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        self.assertEqual(product.to_dict()['name'], 'Test Laptop')
        self.assertEqual(product.to_dict()['price'], 999.99)
        self.assertEqual(product.to_dict()['sku'], 'TEST-LAP-001')
        self.assertEqual(product.to_dict()['stock_quantity'], 10)

    def test_to_dict_returns_copy(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        d1 = product.to_dict()
        d1['name'] = 'Modified'
        d2 = product.to_dict()
        self.assertEqual(d2['name'], 'Test Laptop')

    def test_from_dict_adds_timestamps_if_missing(self):
        data = {k: v for k, v in VALID_PRODUCT_DATA.items()
                if k not in ('created_at', 'updated_at')}
        product = Product.from_dict(data)
        d = product.to_dict()
        self.assertIsNotNone(d.get('created_at'))
        self.assertIsNotNone(d.get('updated_at'))


class TestProductValidate(unittest.TestCase):

    def test_validate_accepts_valid_product(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        valid, errors = product.validate()
        self.assertTrue(valid, f"Expected valid, got errors: {errors}")
        self.assertEqual(errors, [])

    def test_validate_rejects_missing_name(self):
        data = {**VALID_PRODUCT_DATA, 'name': ''}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)
        self.assertIn('name', errors)

    def test_validate_rejects_missing_description(self):
        data = {**VALID_PRODUCT_DATA, 'description': None}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)
        self.assertIn('description', errors)

    def test_validate_rejects_missing_price(self):
        data = {**VALID_PRODUCT_DATA, 'price': None}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)
        self.assertIn('price', errors)

    def test_validate_rejects_missing_sku(self):
        data = {**VALID_PRODUCT_DATA, 'sku': ''}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)
        self.assertIn('sku', errors)

    def test_validate_rejects_invalid_condition(self):
        data = {**VALID_PRODUCT_DATA, 'condition': 'refurbished'}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)

    def test_validate_rejects_missing_multiple_fields(self):
        data = {**VALID_PRODUCT_DATA, 'name': '', 'brand': '', 'category': ''}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertFalse(valid)
        self.assertIn('name', errors)

    def test_validate_used_condition_is_valid(self):
        data = {**VALID_PRODUCT_DATA, 'condition': 'used'}
        product = Product.from_dict(data)
        valid, errors = product.validate()
        self.assertTrue(valid, f"Expected valid for 'used' condition, got: {errors}")


class TestSeedData(unittest.TestCase):

    def test_seed_has_at_least_5_products(self):
        self.assertGreaterEqual(len(SAMPLE_PRODUCTS), 5)

    def test_all_seed_products_have_at_least_8_attributes(self):
        required_keys = ['name', 'description', 'price', 'category', 'brand',
                         'sku', 'stock_quantity', 'condition']
        for product in SAMPLE_PRODUCTS:
            present = [k for k in required_keys if k in product and product[k] is not None]
            self.assertGreaterEqual(
                len(present), 8,
                f"Product '{product.get('name')}' has only {len(present)} of 8 required attributes"
            )

    def test_all_seed_products_have_12_attributes(self):
        for product in SAMPLE_PRODUCTS:
            for field in Product.FIELDS:
                self.assertIn(
                    field, product,
                    f"Seed product '{product.get('name')}' is missing field '{field}'"
                )

    def test_seed_products_pass_validation(self):
        for p_data in SAMPLE_PRODUCTS:
            product = Product.from_dict(p_data)
            valid, errors = product.validate()
            self.assertTrue(
                valid,
                f"Seed product '{p_data.get('name')}' failed validation: {errors}"
            )


class TestProductWithMongomock(unittest.TestCase):

    def setUp(self):
        self.client = mongomock.MongoClient()
        self.db = self.client['test_electroswap']
        self.collection = self.db['products']

    def tearDown(self):
        self.client.close()

    def test_insert_and_retrieve_product(self):
        product = Product.from_dict(VALID_PRODUCT_DATA)
        result = self.collection.insert_one(product.to_dict())
        self.assertIsNotNone(result.inserted_id)

        retrieved = self.collection.find_one({'sku': 'TEST-LAP-001'})
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], 'Test Laptop')
        self.assertEqual(retrieved['price'], 999.99)

    def test_insert_all_seed_products(self):
        from seed_data import seed
        seed(self.db)
        count = self.collection.count_documents({})
        self.assertGreaterEqual(count, 5)

    def test_query_by_category(self):
        for p in SAMPLE_PRODUCTS:
            self.collection.insert_one(p.copy())
        laptops = list(self.collection.find({'category': 'Laptops'}))
        self.assertGreater(len(laptops), 0)
        for lap in laptops:
            self.assertEqual(lap['category'], 'Laptops')

    def test_query_by_condition(self):
        for p in SAMPLE_PRODUCTS:
            self.collection.insert_one(p.copy())
        new_products = list(self.collection.find({'condition': 'new'}))
        used_products = list(self.collection.find({'condition': 'used'}))
        self.assertGreater(len(new_products), 0)
        self.assertGreater(len(used_products), 0)


if __name__ == '__main__':
    unittest.main()
