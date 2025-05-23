# app/routers/__init__.py
from .auth import router as auth_router

# Solo exportar auth si lo mantienes para autenticación
router = [auth_router]

__all__ = ["auth"]