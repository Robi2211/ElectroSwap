"""Main blueprint – homepage and static pages."""

import os
import socket
from flask import Blueprint, render_template, jsonify

from app import db

main_bp = Blueprint("main", __name__, template_folder="../templates/main")


@main_bp.route("/node")
def node_info():
    """Shows which node handled this request – for horizontal scaling demo."""
    return jsonify({
        "node": os.environ.get("NODE_NAME", socket.gethostname()),
    })


@main_bp.route("/")
def index():
    """Homepage – featured products and categories."""
    featured = list(db.products.find().sort("created_at", -1).limit(8))
    categories = db.products.distinct("category")
    return render_template("index.html", featured=featured, categories=categories)
