import traceback
from fastapi import FastAPI
from app.api import auth, assignments
from app.db import base  # noqa: F401  -- loads all models into the registry
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError
from app.core.logging import get_logger

logger = get_logger("api", category="api")


app = FastAPI(
    title="ODMS Backend",
    description="Radiant Pharmaceuticals — Outbound Delivery Management System",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(assignments.router)

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