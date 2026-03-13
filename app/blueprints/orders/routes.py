from flask import Blueprint, render_template

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/')
def list_orders():
    return render_template('orders/list.html', orders=[])


@orders_bp.route('/<order_id>')
def order_detail(order_id):
    return render_template('orders/detail.html', order=None, order_id=order_id)
