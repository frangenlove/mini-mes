from app.db import SessionLocal
from app.models.user import User


with SessionLocal() as db:
    if not db.query(User).filter_by(username="admin").first():
        db.add(User(username="admin",hashed_password="dev-placeholder",role="admin"))
        db.commit()
        print("seeded admin")