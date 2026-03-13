from flask import Blueprint, render_template, current_app

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def dashboard():
    db = current_app.extensions['mongo_db']
    product_count = db.products.count_documents({})
    return render_template('admin/dashboard.html', product_count=product_count)
