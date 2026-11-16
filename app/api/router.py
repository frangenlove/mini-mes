"""
等于@RequestMapping的前缀集合
"""

from fastapi import APIRouter
from app.api.routes import health
from app.api.routes import tickets

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(tickets.router)