# Initializes the FastAPI application.

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from .configs.const import OPEN_API_DESCRIPTION, OPEN_API_TITLE
from .configs.env import settings
from .configs.migrate import migrate_tables
from .configs.version import __version__
from .dependencies import get_query_token, get_token_header
from .internal import admin
from .middleware import log_middleware
from .routers import hero, items, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await migrate_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
# app = FastAPI(dependencies=[Depends(get_query_token)])

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

# Include all routers in here
app.include_router(users.router)
app.include_router(items.router)
app.include_router(hero.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.exception_handler(Exception)
async def universal_exception_handler(_, exc):
    return JSONResponse(content={'detail': f'{type(exc).__name__}: {exc}'}, status_code=500)


@app.get("/", include_in_schema=False)
async def root():
    # """
    # # Redirect
    # to documentation (`/docs/`).
    # """
    # return RedirectResponse(url="/docs/")
    return {"message": "Server is Running..."}
