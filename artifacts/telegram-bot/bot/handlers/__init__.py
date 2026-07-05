from aiogram import Router
from .start import router as start_router
from .menu import router as menu_router
from .luckyjet import router as luckyjet_router
from .rocketqueen import router as rocketqueen_router
from .mines import router as mines_router
from .profile import router as profile_router
from .premium import router as premium_router
from .admin import router as admin_router

def get_main_router() -> Router:
    router = Router()
    router.include_router(start_router)
    router.include_router(menu_router)
    router.include_router(luckyjet_router)
    router.include_router(rocketqueen_router)
    router.include_router(mines_router)
    router.include_router(profile_router)
    router.include_router(premium_router)
    router.include_router(admin_router)
    return router

__all__ = ["get_main_router"]
