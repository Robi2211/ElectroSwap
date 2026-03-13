from flask import Blueprint, render_template

reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@reviews_bp.route('/')
def list_reviews():
    return render_template('reviews/list.html', reviews=[])


@reviews_bp.route('/product/<product_id>')
def product_reviews(product_id):
    return render_template('reviews/list.html', reviews=[], product_id=product_id)
