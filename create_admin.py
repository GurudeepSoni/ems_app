from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    existing_admin = User.query.filter_by(email="admin@test.com").first()
    if not existing_admin:
        admin = User(
            email="admin@test.com",
            password=generate_password_hash("12345", method="sha256"),
            is_admin=True,
            name="Super Admin",
            phone="9999999999",
            alt_phone="8888888888",
            alt_relation="Brother",
            address="Admin City"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    else:
        print("Admin user already exists.")
