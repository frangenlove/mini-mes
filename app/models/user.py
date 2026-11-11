from datetime import datetime
from sqlalchemy import DateTime,String,func
from sqlalchemy.orm import Mapped,mapped_column

from app.db import Base

"""
Java PO
"""
class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(primary_key=True)
    username : Mapped[str] = mapped_column(String(50),unique=True,index=True)
    hashed_password : Mapped[str] = mapped_column(String(255))
    role : Mapped[str] = mapped_column(String(20),default="operator") # admin / operator
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())