"""
等于@RequestMapping的前缀集合
"""

from fastapi import APIRouter
from app.api.routes import health

api_router = APIRouter()
api_router.include_router(health.router)