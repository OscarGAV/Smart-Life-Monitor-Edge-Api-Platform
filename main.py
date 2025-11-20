"""
Smart LifeWatching - Edge API
Vital Monitoring Bounded Context

Author: Oscar Gabriel Aranda Vallejos
Company: Smart Lifemonitor, Inc.
Description: Edge API for IoT vital parameters monitoring with DDD + CQRS
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import uvicorn

from vital_monitoring.application.commands.record_vitals_reading_command import (
    RecordVitalReadingCommand,
    RecordVitalReadingCommandHandler
)
from vital_monitoring.application.queries.get_device_status_query import (
    GetDeviceStatusQuery,
    GetDeviceStatusQueryHandler
)
from vital_monitoring.application.queries.get_vital_history_query import (
    GetVitalHistoryQuery,
    GetVitalHistoryQueryHandler
)
from vital_monitoring.infrastructure.dtos.vitals_reading_dto import VitalReadingDto
from vital_monitoring.infrastructure.persistence.in_memory_vitals_repository import (
    InMemoryVitalRepository
)

# Shared repository instance (in production, use dependency injection)
vital_repository = InMemoryVitalRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("Starting Smart LifeWatching Edge API...")
    print("Vital Monitoring Bounded Context initialized")
    yield
    print("Shutting down Edge API...")


app = FastAPI(
    title="Smart LifeWatching Edge API",
    description="Edge API for IoT Vital Parameters Monitoring with DDD + CQRS",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration for IoT devices
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify device origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "service": "Smart LifeWatching Edge API",
        "status": "operational",
        "bounded_context": "Vital Monitoring",
        "architecture": "DDD + CQRS",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "repository": "operational",
            "command_handlers": "operational",
            "query_handlers": "operational"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# COMMAND ENDPOINTS (Write Operations)
# ============================================================================

@app.post(
    "/api/v1/vital-monitoring/readings",
    status_code=status.HTTP_201_CREATED,
    tags=["Commands"],
    summary="Record a new vital reading from IoT device"
)
async def record_vital_reading(dto: VitalReadingDto):
    """
    Command: Record vital reading from IoT device

    This endpoint receives vital parameters (weight and heart rate) from
    the Smart LifeWatching device and processes them through CQRS command handler.

    Args:
        dto: VitalReadingDto containing device_id, weight, heart_rate

    Returns:
        Command execution result with reading_id
    """
    try:
        # Create command
        command = RecordVitalReadingCommand(
            device_id=dto.device_id,
            weight_kg=dto.weight_kg,
            heart_rate_bpm=dto.heart_rate_bpm
        )

        # Execute command through handler
        handler = RecordVitalReadingCommandHandler(vital_repository)
        result = await handler.handle(command)

        return {
            "success": True,
            "message": "Vital reading recorded successfully",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# QUERY ENDPOINTS (Read Operations)
# ============================================================================

@app.get(
    "/api/v1/vital-monitoring/devices/{device_id}/status",
    tags=["Queries"],
    summary="Get current device status"
)
async def get_device_status(device_id: str):
    """
    Query: Get current device status and latest reading

    Returns the most recent vital reading and device status information.

    Args:
        device_id: Unique identifier of the IoT device

    Returns:
        Device status with latest vital parameters
    """
    try:
        # Create query
        query = GetDeviceStatusQuery(device_id=device_id)

        # Execute query through handler
        handler = GetDeviceStatusQueryHandler(vital_repository)
        result = await handler.handle(query)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device {device_id} not found or has no readings"
            )

        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get(
    "/api/v1/vital-monitoring/devices/{device_id}/history",
    tags=["Queries"],
    summary="Get vital readings history"
)
async def get_vital_history(device_id: str, limit: int = 50):
    """
    Query: Get historical vital readings for a device

    Returns a list of vital readings ordered by timestamp (most recent first).

    Args:
        device_id: Unique identifier of the IoT device
        limit: Maximum number of readings to return (default: 50)

    Returns:
        List of vital readings with timestamps
    """
    try:
        # Create query
        query = GetVitalHistoryQuery(device_id=device_id, limit=limit)

        # Execute query through handler
        handler = GetVitalHistoryQueryHandler(vital_repository)
        result = await handler.handle(query)

        return {
            "success": True,
            "data": {
                "device_id": device_id,
                "readings_count": len(result),
                "readings": result
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# DEVICE INTEGRATION ENDPOINTS
# ============================================================================

@app.post(
    "/api/v1/iot/vital-data",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["IoT Integration"],
    summary="Simplified endpoint for IoT device data submission"
)
async def receive_iot_data(
        device_id: str,
        weight: float,
        heart_rate: int,
        status: str
):
    """
    Simplified endpoint for Arduino/ESP devices

    Accepts form parameters for easier integration with IoT devices
    that may have limited HTTP client capabilities.

    Args:
        device_id: Device identifier
        weight: Weight in kilograms
        heart_rate: Heart rate in BPM
        status: Heart rate status (Low/Normal/High)

    Returns:
        Acceptance confirmation
    """
    try:
        # Convert to DTO
        dto = VitalReadingDto(
            device_id=device_id,
            weight_kg=weight,
            heart_rate_bpm=heart_rate
        )

        # Process through command handler
        command = RecordVitalReadingCommand(
            device_id=dto.device_id,
            weight_kg=dto.weight_kg,
            heart_rate_bpm=dto.heart_rate_bpm
        )

        handler = RecordVitalReadingCommandHandler(vital_repository)
        result = await handler.handle(command)

        return {
            "accepted": True,
            "reading_id": result["reading_id"],
            "message": "Data received and processed"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )