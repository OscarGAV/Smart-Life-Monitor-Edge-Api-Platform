"""
Application Layer - Data Transfer Objects (DTOs)

DTOs are used for API contracts and data transfer between layers.
They are separate from domain entities to maintain clean architecture.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class VitalReadingDto(BaseModel):
    """
    DTO for receiving vital reading data from IoT devices

    This DTO validates incoming data from the API and provides
    a clear contract for external systems.

    Attributes:
        device_id: Unique identifier of the IoT device
        weight_kg: Patient's weight in kilograms (0-300)
        heart_rate_bpm: Heart rate in beats per minute (30-220)
    """

    device_id: str = Field(
        ...,
        description="Unique identifier of the IoT device",
        min_length=1,
        max_length=100,
        example="DEVICE-001"
    )

    weight_kg: float = Field(
        ...,
        description="Patient's weight in kilograms",
        ge=0,
        le=300,
        example=75.5
    )

    heart_rate_bpm: int = Field(
        ...,
        description="Heart rate in beats per minute",
        ge=30,
        le=220,
        example=72
    )

    @validator('device_id')
    def validate_device_id(cls, v):
        """Validate device_id is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError('device_id cannot be empty')
        return v.strip()

    @validator('weight_kg')
    def validate_weight(cls, v):
        """Validate weight is realistic"""
        if v < 0:
            raise ValueError('Weight cannot be negative')
        if v > 300:
            raise ValueError('Weight exceeds maximum realistic value')
        return round(v, 1)  # Round to 1 decimal place

    @validator('heart_rate_bpm')
    def validate_heart_rate(cls, v):
        """Validate heart rate is within physiological bounds"""
        if v < 30:
            raise ValueError('Heart rate too low (minimum: 30 BPM)')
        if v > 220:
            raise ValueError('Heart rate too high (maximum: 220 BPM)')
        return v

    class Config:
        schema_extra = {
            "example": {
                "device_id": "LIFEWATCHING-001",
                "weight_kg": 75.3,
                "heart_rate_bpm": 72
            }
        }


class DeviceStatusDto(BaseModel):
    """
    DTO for device status response

    Used to return device status information to API consumers.
    """

    device_id: str
    is_active: bool
    last_contact: str
    total_readings: int
    current_weight_kg: Optional[float]
    current_heart_rate_bpm: Optional[int]
    heart_rate_status: Optional[str]
    weight_alert: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "device_id": "LIFEWATCHING-001",
                "is_active": True,
                "last_contact": "2025-11-19T10:30:00Z",
                "total_readings": 156,
                "current_weight_kg": 75.3,
                "current_heart_rate_bpm": 72,
                "heart_rate_status": "Normal",
                "weight_alert": "Normal"
            }
        }