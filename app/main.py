# Initializes the FastAPI application.

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.api import set_items_transformer

from .core import config
from .core.database import init_db, sessionmanager
from .middleware import register_middleware
from .routers.base import register_all_routers
from .utils.exceptions import register_all_errors

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # await init_db()
#     yield
#     if sessionmanager._engine is not None:
#         # Close the DB connection
#         await sessionmanager.close()

app = FastAPI(
    # lifespan=lifespan,
    title=config.settings.OPEN_API_TITLE,
    description=config.settings.OPEN_API_DESCRIPTION,
    version=config.settings.APP_VERSION,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Farrid Putra",
        "url": "https://github.com/bonkx",
        "email": "farridputra@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{config.settings.API_PREFIX}/openapi.json",
    docs_url=f"{config.settings.API_PREFIX}/docs",
    redoc_url=f"{config.settings.API_PREFIX}/redoc"
)

# register all Exceptions
register_all_errors(app)

register_middleware(app)

# register all routers
register_all_routers(app)

# This should be done after all calls to app.include_router()
# Pagination
add_pagination(app)  # important! add pagination to your app
# set globally pagination Items transformer
# set_items_transformer(lambda items: [item.model_dump() for item in items])
