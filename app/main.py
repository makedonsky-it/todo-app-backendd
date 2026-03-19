import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()

settings = get_settings()
app = FastAPI()
logger = logging.getLogger("app.middleware")  # Название логгера в логах

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

cnt = 0


# Выполняется до и после обработки каждого HTTP-запроса.
@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)  # Работа самого эндпоинта
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.middleware("http")
async def http_counter(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    global cnt
    cnt += 1
    response: Response = await call_next(request)
    response.headers["X-Request-Number"] = str(cnt)
    return response


app.include_router(api_router)
