import traceback
from fastapi import FastAPI
from app.db import base  # noqa: F401  -- loads all models into the registry
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from app.core.logging import get_logger
from app.core.exceptions import AppError
from app.api.v1 import router as api_v1_router

logger = get_logger("api", category="api")


app = FastAPI(
    title="ODMS Backend",
    description="Radiant Pharmaceuticals — Outbound Delivery Management System",
    version="0.1.0",
    docs_url=None, 
    redoc_url=None,
    author="Najmul Islam",
)

app.include_router(api_v1_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"status": "ok", "service": "ODMS Backend"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Return HTTP errors in the standard response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Return service-layer errors in the standard response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.message, "data": None}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return validation errors in the standard response format."""
    # Extract the first readable error message
    errors = exc.errors()
    message = "Validation error"
    if errors:
        first = errors[0]
        field = ".".join(str(x) for x in first.get("loc", []) if x != "body")
        message = f"{field}: {first.get('msg', 'invalid')}"
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": message, "data": None},
    )
    
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors, returned in the standard format."""
    logger.error(
        f"Unhandled error on {request.method} {request.url.path}: "
        f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Something went wrong. Please try again.",
            "data": None,
        },
    )
    
@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url="/static/images/odms.png" 
    )

@app.get("/api/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_favicon_url="/static/images/odms.png"
    )