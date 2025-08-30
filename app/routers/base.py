from fastapi import FastAPI

from ..core.config import settings
from ..internal import admin_router
from . import (account_router, auth_router, hero_publisher_router, hero_router,
               misc_router, web_router)


def register_all_routers(app: FastAPI):

    # Include all routers in here

    # api urls
    app.include_router(auth_router.router, prefix=f"{settings.API_PREFIX}/auth", tags=["authentications"])
    app.include_router(account_router.router, prefix=f"{settings.API_PREFIX}/account", tags=["accounts"])
    app.include_router(misc_router.upload_router, prefix=f"{settings.API_PREFIX}/upload", tags=["miscs"])

    app.include_router(hero_publisher_router.router, prefix=f"{settings.API_PREFIX}/hero-publishers", tags=["hero publishers"])
    app.include_router(hero_router.router, prefix=f"{settings.API_PREFIX}/heroes", tags=["heroes"])

    # web urls
    app.include_router(web_router.home_router)
    app.include_router(web_router.account_router, prefix=f"/account", tags=["web urls"])

    # admin urls (internal)
    app.include_router(
        admin_router.router,
        prefix=f"/admin",
        responses={418: {"description": "I'm a teapot"}},
    )
