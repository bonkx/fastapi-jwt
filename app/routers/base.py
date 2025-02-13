from fastapi import FastAPI

from ..core.config import settings
from ..internal import admin
from . import hero_publisher_route, hero_route, users_route


def register_all_routers(app: FastAPI):

    # Include all routers in here
    app.include_router(users_route.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
    app.include_router(hero_publisher_route.router, prefix=f"{settings.API_PREFIX}/hero-publishers", tags=["hero_publishers"])
    app.include_router(hero_route.router, prefix=f"{settings.API_PREFIX}/heroes", tags=["heroes"])
    # app.include_router(
    #     admin.router,
    #     prefix="/admin",
    #     tags=["admin"],
    #     # dependencies=[Depends(get_token_header)],
    #     responses={418: {"description": "I'm a teapot"}},
    # )
