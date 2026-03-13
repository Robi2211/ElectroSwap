from datetime import datetime, timezone


class Product:
    FIELDS = [
        'name',
        'description',
        'price',
        'category',
        'brand',
        'sku',
        'stock_quantity',
        'condition',
        'weight',
        'image_url',
        'created_at',
        'updated_at',
    ]

    REQUIRED_FIELDS = [
        'name',
        'description',
        'price',
        'category',
        'brand',
        'sku',
        'stock_quantity',
        'condition',
    ]

    def __init__(self, data: dict):
        self._data = data.copy()

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        now = datetime.now(timezone.utc)
        product_data = {field: data.get(field) for field in cls.FIELDS}
        if not product_data.get('created_at'):
            product_data['created_at'] = now
        if not product_data.get('updated_at'):
            product_data['updated_at'] = now
        return cls(product_data)

    def to_dict(self) -> dict:
        return self._data.copy()

    def validate(self) -> tuple[bool, list[str]]:
        missing = [f for f in self.REQUIRED_FIELDS if not self._data.get(f)]
        if missing:
            return False, missing
        errors = []
        if self._data.get('price') is not None:
            try:
                price = float(self._data['price'])
                if price < 0:
                    errors.append('price must be non-negative')
            except (ValueError, TypeError):
                errors.append('price must be a number')
        if self._data.get('stock_quantity') is not None:
            try:
                qty = int(self._data['stock_quantity'])
                if qty < 0:
                    errors.append('stock_quantity must be non-negative')
            except (ValueError, TypeError):
                errors.append('stock_quantity must be an integer')
        if self._data.get('condition') not in (None, 'new', 'used'):
            errors.append('condition must be "new" or "used"')
        if errors:
            return False, errors
        return True, []

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"Product has no attribute '{name}'")
