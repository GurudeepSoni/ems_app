from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # LOGIN DATA
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # PERSONAL DATA
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    alt_phone = db.Column(db.String(20))
    alt_relation = db.Column(db.String(50))
    address = db.Column(db.String(300))
    photo_filename = db.Column(db.String(200))

    def __repr__(self):
        return f"<User {self.email}>"
