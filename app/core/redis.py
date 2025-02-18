import redis.asyncio as aioredis  # type: ignore

from .config import settings

token_blocklist = aioredis.from_url(settings.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60))  # multiply minutes to seconds


async def token_in_blocklist(jti: str) -> bool:
    jti = await token_blocklist.get(jti)

    return jti is not None
