from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import sentry_sdk
from kafka_service.kafka_service import (
     auth_events
    )
from settings import (
    CORS_ALLOWED_ORIGINS,
    SENTRY_DSN,
    SENTRY_TRACES_SAMPLE_RATES,
    FILE_STORAGE_ADAPTER,
    ENVIRONTMENT
)
from core.logging_config import logger
from routes.auth import router as auth_router
from routes.auth import router as auth_router
from routes.tenant import router as tenant_router
import asyncio
from redis_client import shutdown,startup

if SENTRY_DSN != None:  # NOQA
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATES,
    )

# END OF INISIALISASI CRONJOB
    # --- shutdown ---
if ENVIRONTMENT == 'dev':
    app = FastAPI(
        title="PDP Multitenant",
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_ui_init_oauth={
            "clientId": "your-client-id",
            "authorizationUrl": "/auth/token",
            "tokenUrl": "/auth/token",
        },
    )
elif ENVIRONTMENT == 'prod':
        app = FastAPI(
        title="PDP Multitenant",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_ui_init_oauth={
            "clientId": "your-client-id",
            "authorizationUrl": "/auth/token",
            "tokenUrl": "/auth/token",
        },
    )
app.add_middleware(
    CORSMiddleware,
    # allow_origins=CORS_ALLOWED_ORIGINS,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if FILE_STORAGE_ADAPTER != 'minio':
    app.mount("/static", StaticFiles(directory="static"))

@app.get("/")
async def hello():
    return {"Hello": "from Patuh PDP Telkom Sigma", "service": "auth-consumer"}


app.include_router(auth_router, prefix="/auth")
app.include_router(tenant_router, prefix="/tenant")


# @app.on_event("startup")
# async def startup_event():
#     await startup()
#     loop = asyncio.get_running_loop()
#     loop.create_task(run_all_consumers())

# @app.on_event("shutdown")
# async def on_shutdown():
#     await shutdown()

# async def run_all_consumers():
#     await asyncio.gather(
#         auth_events(),
#     )