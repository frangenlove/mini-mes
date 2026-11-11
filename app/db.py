"""
Connection layer
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

"""
pool_pre_ping=True: 连接池里拿到的连接先探活，防止数据库重启后拿到死连接(约等于连接池的testOnBorrow)
"""
engine = create_engine(settings.database_url, pool_pre_ping=True, echo=settings.debug)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

"""
Base是所有模型的父类，Alembic靠它的metadata知道有哪些表
"""
class Base(DeclarativeBase):
    pass

"""
生成器,yield前是前置，后是清理
FastAPI的Depends会在请求结束时自动执行finally
"""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()