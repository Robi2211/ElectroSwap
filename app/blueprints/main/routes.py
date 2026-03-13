from flask import Blueprint, render_template, current_app
from bson import ObjectId

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    db = current_app.extensions['mongo_db']
    featured = list(db.products.find().limit(6))
    for p in featured:
        p['_id'] = str(p['_id'])
    return render_template('main/index.html', featured_products=featured)
