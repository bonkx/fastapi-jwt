from fastapi import FastAPI

from ..core.config import settings
from ..internal import admin
from . import employee, hero, users


def register_all_routers(app: FastAPI):

    # Include all routers in here
    app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
    app.include_router(hero.router, prefix=f"{settings.API_PREFIX}/heroes", tags=["heroes"])
    app.include_router(employee.router, prefix=f"{settings.API_PREFIX}/employees", tags=["employees"])
    app.include_router(
        admin.router,
        prefix="/admin",
        tags=["admin"],
        # dependencies=[Depends(get_token_header)],
        responses={418: {"description": "I'm a teapot"}},
    )
