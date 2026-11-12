from fastapi import APIRouter

from app.api.v1.app import router as app_router

# Version 1 of the API. Admin and depot routers will be added here later.
router = APIRouter(prefix="/api/v1")
router.include_router(app_router)