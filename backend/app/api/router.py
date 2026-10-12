from fastapi import APIRouter

from app.api import google, health, task

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(task.router)
api_router.include_router(google.router)

# Register new route modules here, e.g.:
# api_router.include_router(tasks.router, dependencies=[Depends(get_current_user)])
