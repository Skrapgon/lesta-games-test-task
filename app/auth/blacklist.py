from redis import Redis
import redis.asyncio as redis
from jose import jwt
from datetime import timezone, datetime

from core.config import SECRET_KEY, ALGORITHM, REDIS_URL

redis_client: Redis = redis.from_url(REDIS_URL)

BLACKLIST_PREFIX = 'token:blacklist:'

async def add_blacklist_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp_timestamp = payload.get('exp', 0)
        if exp_timestamp:
            now = datetime.now(timezone.utc).timestamp()
            ttl = max(int(exp_timestamp - now), 0)

            key = f'{BLACKLIST_PREFIX}{token}'
            await redis_client.set(key, '1', ex=ttl)
            return True
        return False
    except Exception:
        return False

async def is_blacklisted_token(token: str) -> bool:
    key = f'{BLACKLIST_PREFIX}{token}'
    return await redis_client.exists(key) == 1