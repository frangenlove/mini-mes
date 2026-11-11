from datetime import datetime
from sqlalchemy import DateTime,String,ForeignKey,Text,func
from sqlalchemy.orm import Mapped,mapped_column

from app.db import Base

"""
status不用PG原生enum，因为原生enum在Alembic里增删很麻烦（要手写ALTER TYPE）
先用String(20)+应用层StrEunm约束.Well,this is just a engineering tradeoff
"""
class Ticket(Base):
    __tablename__ = "tickets"

    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(200),index=True)
    description : Mapped[str | None] = mapped_column(Text,nullable=True)
    status : Mapped[str] = mapped_column(String(20),default="pending",index=True)
    priority : Mapped[int] = mapped_column(default=3)
    created_by : Mapped[int] = mapped_column(ForeignKey("users.id"),index=True)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at : Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),onupdate=func.now(),nullable=True
    )