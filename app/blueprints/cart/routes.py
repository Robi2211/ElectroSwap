from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app
from bson import ObjectId

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/')
def view_cart():
    cart = session.get('cart', [])
    return render_template('cart/cart.html', cart=cart)


@cart_bp.route('/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    flash('Added to cart!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))


@cart_bp.route('/remove/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
    session['cart'] = cart
    return redirect(url_for('cart.view_cart'))
