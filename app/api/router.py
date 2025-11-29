from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.dashboards.router import router as dashboards_router
from app.modules.lspop.router import router as lspop_router
from app.modules.dropdown.router import router as dropdown_router
from app.modules.spop.router import router as spop_router
from app.modules.sppt.router import router as sppt_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(dashboards_router)
api_router.include_router(sppt_router)
api_router.include_router(spop_router)
api_router.include_router(lspop_router)
api_router.include_router(dropdown_router)
