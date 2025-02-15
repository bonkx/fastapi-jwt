# global exceptions

from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError, SQLAlchemyError


class ResponseException(HTTPException):
    """Custom Response Exception"""

    def __init__(
        self,
        status_code: int,
        detail: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        resolution: Optional[Any] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.resolution = resolution


class BaseException(Exception):
    """This is the base class for all bookly errors"""

    pass


class InvalidToken(BaseException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BaseException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(BaseException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(BaseException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(BaseException):
    """User has provided an email for a user who exists during sign up."""

    pass


class UsernameAlreadyExists(BaseException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(BaseException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(BaseException):
    """User does not have the neccessary permissions to perform an action."""

    pass


class TagAlreadyExists(BaseException):
    """Tag already exists"""

    pass


class UserNotFound(BaseException):
    """User Not found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BaseException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "detail": "User with the email already exists",
                "resolution": "Try again with another Email",
                # "error_code": "user_exists",
            },
        ),
    )

    app.add_exception_handler(
        UsernameAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "detail": "User with the username already exists",
                "resolution": "Try again with another Username"
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "detail": "User not found",
                # "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "detail": "Invalid Email Or Password",
                # "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Token is invalid Or expired",
                "resolution": "Please get new token",
                # "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                # "error_code": "token_revoked",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "Please provide a valid access token",
                "resolution": "Please get an access token",
                # "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "detail": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                # "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "detail": "You do not have enough permissions to perform this action",
                # "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "detail": "Tag Already exists",
                # "error_code": "tag_exists",
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "detail": "Account Not verified",
                "resolution": "Please check your email for verification details"
                # "error_code": "account_not_verified",
            },
        ),
    )

    @app.exception_handler(ResponseException)
    async def universal_exception_handler(_, exc: ResponseException):
        content = {
            "detail": f'{exc.detail}',
            # "error_code": f'{exc.status_code}',
        }
        if exc.resolution:
            content["resolution"] = exc.resolution

        # "exc": f'{type(exc).__name__}: {exc}',

        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "detail": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # @app.exception_handler(SQLAlchemyError)
    # async def database__error(request, exc):
    #     print(str(exc))
    #     return JSONResponse(
    #         content={
    #             "detail": "Oops! Something went wrong",
    #             "error_code": "server_error",
    #         },
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )
