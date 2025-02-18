# # Defines functions for authentication.

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from passlib.context import CryptContext

from ..logger import logging
from .config import settings


@dataclass
class SolveBugBcryptWarning:
    # Warning about missing `bcrypt.__about__`, after upgrading bcrypt from 4.0.1 to 4.1.1
    __version__: str = getattr(bcrypt, "__version__")


setattr(bcrypt, "__about__", SolveBugBcryptWarning())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash a password using bcrypt
async def generate_passwd_hash(password: str) -> str:
    return pwd_context.hash(password)


# Check if the provided password matches the stored password (hashed)
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_url_safe_token(data: dict):
    token = jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


async def decode_url_safe_token(token: str):
    try:
        token_data = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return token_data
    except Exception as e:
        logging.error(str(e))
        raise Exception(str(e))


async def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now(UTC) + (
        expiry if expiry is not None else timedelta(seconds=(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))
    )
    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token


async def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError as e:
        logging.error(str(e))
        return None

# def create_access_token(subject: str | Any, expires_delta: timedelta = None) -> str:
#     if expires_delta:
#         expire = datetime.now(datetime.timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(datetime.timezone.utc) + timedelta(
#             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
#         )
#     to_encode = {"exp": expire, "sub": str(subject), "type": "access"}

#     return jwt.encode(
#         payload=to_encode,
#         key=settings.ENCRYPT_KEY,
#         algorithm=JWT_ALGORITHM,
#     )


# def create_refresh_token(subject: str | Any, expires_delta: timedelta = None) -> str:
#     if expires_delta:
#         expire = datetime.now(datetime.timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(datetime.timezone.utc) + timedelta(
#             minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS
#         )
#     to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}

#     return jwt.encode(
#         payload=to_encode,
#         key=settings.ENCRYPT_KEY,
#         algorithm=JWT_ALGORITHM,
#     )


# def decode_token(token: str) -> dict[str, Any]:
#     return jwt.decode(
#         jwt=token,
#         key=settings.ENCRYPT_KEY,
#         algorithms=[JWT_ALGORITHM],
#     )


# def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
#     if isinstance(plain_password, str):
#         plain_password = plain_password.encode()
#     if isinstance(hashed_password, str):
#         hashed_password = hashed_password.encode()

#     return bcrypt.checkpw(plain_password, hashed_password)


# def get_password_hash(plain_password: str | bytes) -> str:
#     if isinstance(plain_password, str):
#         plain_password = plain_password.encode()

#     return bcrypt.hashpw(plain_password, bcrypt.gensalt()).decode()


# def get_data_encrypt(data) -> str:
#     data = fernet.encrypt(data)
#     return data.decode()


# def get_content(variable: str) -> str:
#     return fernet.decrypt(variable.encode()).decode()
