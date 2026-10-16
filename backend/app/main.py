import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from . import __version__
from .config import settings
from .routers import appointments, doctors, system

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

# Schema is strictly managed through Alembic migrations executed in entrypoint, never create_all()
app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="ClinicPulse Healthcare Scheduling & Patient Flow Platform — DevOps Capstone.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(doctors.router)
app.include_router(appointments.router)

# Expose HTTP traffic metrics for Prometheus scraping on /metrics
Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
