"""
程序入口，等于@SpringBootApplication
"""
import logging

from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.router import api_router
from app.core.config import settings

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name,version="0.1.0")
app.include_router(api_router,prefix="/api/v1")

@app.exception_handler(AppError)
async def app_error_handler(request,exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code,
                        content={"error":{"code":exc.code,"message":exc.message}})

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request,exc: RequestValidationError) -> JSONResponse:

    details = [
        {
            "field":".".join(str(x) for x in err["loc"][1:]),
            "message":err["msg"],
        }
        for err in exc.errors()
    ]
    
    return JSONResponse(
        status_code = 422,
        content={"error": {"code": "VALIDATION_ERROR","message": "invalid request","details":details}}
    )

@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request,exc: Exception) -> JSONResponse:
    logger.exception("unhandled error on %s %s",request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error":{"code":"INTERNAL","message": "internal error"}}
    )

def root()->dict:
    return {"app":settings.app_name,"docs":"/docs"}
