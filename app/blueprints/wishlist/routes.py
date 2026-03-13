from flask import Blueprint, render_template, session, redirect, url_for, flash

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')


@wishlist_bp.route('/')
def view_wishlist():
    wishlist = session.get('wishlist', [])
    return render_template('wishlist/wishlist.html', wishlist=wishlist)


@wishlist_bp.route('/add/<product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    wishlist = session.get('wishlist', [])
    if product_id not in wishlist:
        wishlist.append(product_id)
    session['wishlist'] = wishlist
    flash('Added to wishlist!', 'success')
    return redirect(url_for('products.product_detail', product_id=product_id))


@wishlist_bp.route('/remove/<product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    wishlist = session.get('wishlist', [])
    if product_id in wishlist:
        wishlist.remove(product_id)
    session['wishlist'] = wishlist
    return redirect(url_for('wishlist.view_wishlist'))
