from fastapi import FastAPI

from ..core.config import settings
from ..internal import admin
from . import auth, hero_publisher_route, hero_route, users_route


def register_all_routers(app: FastAPI):

    # Include all routers in here
    app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentications"])

    app.include_router(users_route.router, prefix=f"{settings.API_PREFIX}/users", tags=["Users"])
    app.include_router(hero_publisher_route.router, prefix=f"{settings.API_PREFIX}/hero-publishers", tags=["Hero Publishers"])
    app.include_router(hero_route.router, prefix=f"{settings.API_PREFIX}/heroes", tags=["Heroes"])
    app.include_router(
        admin.router,
        prefix=f"/admin",
        # dependencies=[Depends(get_token_header)],
        responses={418: {"description": "I'm a teapot"}},
    )
