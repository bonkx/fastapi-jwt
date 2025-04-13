from fastapi import FastAPI

from ..core.config import settings
from ..internal import admin
from . import (account_route, auth_route, hero_publisher_route, hero_route,
               misc_route, web_route)


def register_all_routers(app: FastAPI):

    # Include all routers in here

    # api urls
    app.include_router(auth_route.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentications"])
    app.include_router(account_route.router, prefix=f"{settings.API_PREFIX}/account", tags=["Accounts"])
    app.include_router(misc_route.upload_router, prefix=f"{settings.API_PREFIX}/upload", tags=["Miscs"])

    app.include_router(hero_publisher_route.router, prefix=f"{settings.API_PREFIX}/hero-publishers", tags=["Hero Publishers"])
    app.include_router(hero_route.router, prefix=f"{settings.API_PREFIX}/heroes", tags=["Heroes"])

    # web urls
    app.include_router(web_route.home_router)
    app.include_router(web_route.account_router, prefix=f"/account", tags=["Web Urls"])

    # admin urls (internal)
    app.include_router(
        admin.router,
        prefix=f"/admin",
        # dependencies=[Depends(get_token_header)],
        responses={418: {"description": "I'm a teapot"}},
    )
