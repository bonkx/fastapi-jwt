import time

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .logger import logger


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start = time.time()

        response = await call_next(request)

        process_time = time.time() - start
        log_dict = {
            'url': request.url.path,
            'method': request.method,
            'process_time': process_time,
        }
        message = f'{request.client.host}:{request.client.port} - "{request.method} {request.url.path}" {response.status_code} - completed after {process_time}'

        # print(message)
        logger.info(message, extra=log_dict)

        return response

    origins = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    allowed_hosts = [
        "test",
        "localhost", "127.0.0.1", "0.0.0.0",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
