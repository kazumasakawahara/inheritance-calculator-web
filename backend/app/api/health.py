"""
Health check endpoints for monitoring and deployment.
Provides basic liveness and detailed readiness checks.
"""
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.config import settings
from app.services.neo4j_service import Neo4jService

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check (liveness probe).
    Returns 200 if the application is running.

    Use this for:
    - Kubernetes liveness probes
    - Docker healthchecks
    - Load balancer health checks
    """
    return {
        "status": "healthy",
        "service": "inheritance-calculator-api"
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Detailed readiness check.
    Verifies database connections and critical services.

    Use this for:
    - Kubernetes readiness probes
    - Pre-deployment validation
    - Monitoring dashboards

    Returns:
        dict: Status of all critical services

    Raises:
        HTTPException: 503 if any critical service is unavailable
    """
    health_status = {
        "status": "ready",
        "service": "inheritance-calculator-api",
        "checks": {
            "database": "unknown",
            "neo4j": "unknown"
        }
    }

    is_ready = True

    # Check PostgreSQL connection
    try:
        async for session in get_async_session():
            result = await session.execute(text("SELECT 1"))
            if result.scalar() == 1:
                health_status["checks"]["database"] = "healthy"
            else:
                health_status["checks"]["database"] = "unhealthy"
                is_ready = False
            break  # Only need one session
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        is_ready = False

    # Check Neo4j connection
    try:
        neo4j_service = Neo4jService()
        await neo4j_service.connect()
        try:
            # Simple connectivity test
            await neo4j_service.driver.verify_connectivity()
            health_status["checks"]["neo4j"] = "healthy"
        finally:
            await neo4j_service.close()
    except Exception as e:
        health_status["checks"]["neo4j"] = f"unhealthy: {str(e)}"
        is_ready = False

    if not is_ready:
        health_status["status"] = "not_ready"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )

    return health_status


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness check (alias for /health).
    Kubernetes-style liveness probe endpoint.
    """
    return {
        "status": "alive",
        "service": "inheritance-calculator-api"
    }
