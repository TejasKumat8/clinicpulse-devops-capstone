from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import __version__
from ..config import settings
from ..db import get_db
from ..schemas import InfoOut

router = APIRouter(tags=["system"])


@router.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": __version__,
        "author": "Tejas Kumat",
        "docs": "/docs",
    }


@router.get("/health")
def health():
    """Liveness probe: verifies the HTTP server process is running and responsive."""
    return {"status": "UP"}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    """Readiness probe: validates database connectivity before admitting live traffic."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "READY"}


@router.get("/api/info", response_model=InfoOut)
def info():
    """Traceability endpoint providing deployed version and Git commit SHA."""
    return InfoOut(
        service=settings.app_name,
        version=__version__,
        gitSha=settings.git_sha,
        environment=settings.environment,
    )
