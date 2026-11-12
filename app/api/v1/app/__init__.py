from fastapi import APIRouter

from app.api.v1.app import assignments, auth, collections, deliveries

# Every endpoint used by the DA mobile app lives under /app
router = APIRouter(prefix="/app")
router.include_router(auth.router)
router.include_router(assignments.router)
router.include_router(deliveries.router)
router.include_router(collections.router)