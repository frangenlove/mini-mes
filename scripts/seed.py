from app.db import SessionLocal
from app.models.user import User
from app.core.security import hash_password


with SessionLocal() as db:
    for name,pwd,role in [("admin","admin123","admin"),("operator","operator123","operator")]:
        user = db.query(User).filter_by(username=name).first()
        if user is None:
            db.add(User(username=name,hashed_password=hash_password(pwd),role=role))
        else:
            user.hashed_password = hash_password(pwd) # 覆盖
            user.role = role
        db.commit()
        print("seeded")