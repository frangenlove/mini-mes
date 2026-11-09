"""
程序入口，等于@SpringBootApplication
"""

from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name,version="0.1.0")
app.include_router(api_router,prefix="/api/v1")

def root()->dict:
    return {"app":settings.app_name,"docs":"/docs"}