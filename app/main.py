# Initializes the FastAPI application.

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi_pagination.api import set_items_transformer
from starlette.responses import RedirectResponse

from .core.const import OPEN_API_DESCRIPTION, OPEN_API_TITLE
from .core.database import init_db
from .core.version import __version__
from .internal import admin
from .middleware import register_middleware
from .routers import employee, hero, users
from .utils.exceptions import register_all_errors

api_version = "v1"
version_prefix = f"/api/{api_version}"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield await init_db()

app = FastAPI(
    lifespan=lifespan,
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Farrid Putra",
        "url": "https://github.com/bonkx",
        "email": "farridputra@gmail.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)

# Pagination
add_pagination(app)  # important! add pagination to your app
# set globally Items transformer
set_items_transformer(lambda items: [item.model_dump() for item in items])

# register all Exceptions
register_all_errors(app)

register_middleware(app)

# Include all routers in here
app.include_router(users.router, prefix=f"{version_prefix}/users", tags=["users"])
app.include_router(hero.router, prefix=f"{version_prefix}/heroes", tags=["heroes"])
app.include_router(employee.router, prefix=f"{version_prefix}/employees", tags=["employees"])
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    # dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/", include_in_schema=False)
async def root():
    # """
    # # Redirect
    # to documentation (`/docs/`).
    # """
    # return RedirectResponse(url="/docs/")
    return {"message": "Server is Running..."}


@app.get("/docs", include_in_schema=False)
async def docs():
    # """
    # # Redirect
    # to documentation (`/docs/`).
    # """
    return RedirectResponse(url=f"{version_prefix}/docs/")
