import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    routes_calls,
    routes_carriers,
    routes_loads,
    routes_metrics,
    routes_negotiate,
)
from app.core.config import get_settings
from app.db.models import Base  # noqa: F401 - ensures tables are registered
from app.db.session import Base as _B, engine  # noqa: F401
from app.seed.seed_loads import seed_if_empty

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("freight-pilot")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "Inbound Carrier Sales API used by the HappyRobot agent and the "
            "Freight Pilot dashboard."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        from app.db.session import Base, engine
        Base.metadata.create_all(bind=engine)
        seed_if_empty()
        log.info("Freight Pilot API ready. env=%s", settings.environment)

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "ok"}

    app.include_router(routes_carriers.router)
    app.include_router(routes_loads.router)
    app.include_router(routes_negotiate.router)
    app.include_router(routes_calls.router)
    app.include_router(routes_metrics.router)

    return app


app = create_app()
