"""User model and helpers for Flask-Login integration with MongoDB."""

from flask_login import UserMixin
from bson import ObjectId

from app import db


class User(UserMixin):
    """Wraps a MongoDB user document for Flask-Login."""

    def __init__(self, user_doc):
        self._doc = user_doc

    @property
    def id(self):
        return str(self._doc["_id"])

    def get_id_object(self):
        """Return the ObjectId for MongoDB queries."""
        return self._doc["_id"]

    @property
    def username(self):
        return self._doc.get("username", "")

    @property
    def email(self):
        return self._doc.get("email", "")

    @property
    def role(self):
        return self._doc.get("role", "customer")

    @property
    def address(self):
        return self._doc.get("address", {})

    @property
    def is_admin(self):
        return self.role == "admin"


def load_user(user_id):
    """Flask-Login user loader callback."""
    try:
        doc = db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    if doc:
        return User(doc)
    return None
