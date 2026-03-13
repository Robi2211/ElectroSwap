from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from app.models.product import Product

products_bp = Blueprint('products', __name__, url_prefix='/products')


@products_bp.route('/')
def list_products():
    db = current_app.extensions['mongo_db']
    category = request.args.get('category')
    query = {'category': category} if category else {}
    products = list(db.products.find(query))
    for p in products:
        p['_id'] = str(p['_id'])
    categories = db.products.distinct('category')
    return render_template('products/list.html', products=products, categories=categories,
                           selected_category=category)


@products_bp.route('/<product_id>')
def product_detail(product_id):
    db = current_app.extensions['mongo_db']
    try:
        oid = ObjectId(product_id)
    except InvalidId:
        flash('Invalid product ID.', 'danger')
        return redirect(url_for('products.list_products'))
    product = db.products.find_one({'_id': oid})
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products.list_products'))
    product['_id'] = str(product['_id'])
    return render_template('products/detail.html', product=product)


@products_bp.route('/add', methods=['GET'])
def add_product_form():
    return render_template('products/add.html')


@products_bp.route('/add', methods=['POST'])
def add_product():
    db = current_app.extensions['mongo_db']
    form_data = {
        'name': request.form.get('name', '').strip(),
        'description': request.form.get('description', '').strip(),
        'price': _parse_float(request.form.get('price')),
        'category': request.form.get('category', '').strip(),
        'brand': request.form.get('brand', '').strip(),
        'sku': request.form.get('sku', '').strip(),
        'stock_quantity': _parse_int(request.form.get('stock_quantity')),
        'condition': request.form.get('condition', '').strip(),
        'weight': _parse_float(request.form.get('weight')),
        'image_url': request.form.get('image_url', '').strip(),
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
    }
    product = Product.from_dict(form_data)
    valid, errors = product.validate()
    if not valid:
        flash(f'Validation errors: {", ".join(errors)}', 'danger')
        return render_template('products/add.html', form_data=form_data)
    db.products.insert_one(product.to_dict())
    flash('Product added successfully!', 'success')
    return redirect(url_for('products.list_products'))


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
