from app.api.routes.attendance import router as attendance_router
from app.api.routes.auth import router as auth_router
from app.api.routes.leave_requests import router as leave_requests_router

__all__ = ["auth_router", "attendance_router", "leave_requests_router"]
