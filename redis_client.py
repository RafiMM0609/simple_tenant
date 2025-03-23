import redis.asyncio as redis
from settings import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB
)

# Buat instance Redis
redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    """Dependency Injection untuk mendapatkan instance Redis."""
    return redis_client

async def startup():
    """Fungsi untuk inisialisasi Redis saat aplikasi FastAPI dimulai."""
    global redis_client
    redis_client = redis.Redis(
        # host='172.16.249.179', 
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB, 
        # password='MXWnhevPbTDNtAqmFQCfZH',
        # decode_responses=True,
    )
    pong = await redis_client.ping()
    print(f"Redis connected: {pong}")  # Harus `True` jika sukses

async def shutdown():
    """Fungsi untuk menutup koneksi Redis saat aplikasi berhenti."""
    if redis_client:
        await redis_client.close()