"""
Domain Layer - Vital Reading Entity
Bounded Context: Vital Monitoring

This is the core domain entity representing a vital parameters reading
from a Smart LifeWatching device.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class HeartRateStatus(Enum):
    """Value Object: Heart Rate Status Classification"""
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"


class WeightAlert(Enum):
    """Value Object: Weight Alert Classification"""
    NORMAL = "Normal"
    OVERWEIGHT = "Overweight"


@dataclass
class VitalReading:
    """
    Aggregate Root: VitalReading

    Represents a single vital parameters reading from an IoT device.
    This is the core domain entity with business rules and invariants.

    Attributes:
        reading_id: Unique identifier for the reading
        device_id: Identifier of the IoT device that generated the reading
        weight_kg: Patient's weight in kilograms
        heart_rate_bpm: Heart rate in beats per minute
        heart_rate_status: Classification of heart rate (Low/Normal/High)
        weight_alert: Weight alert status
        timestamp: When the reading was taken
        recorded_at: When the reading was recorded in the system
    """

    device_id: str
    weight_kg: float
    heart_rate_bpm: int
    reading_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    recorded_at: datetime = field(default_factory=datetime.utcnow)
    heart_rate_status: Optional[HeartRateStatus] = None
    weight_alert: Optional[WeightAlert] = None

    def __post_init__(self):
        """Post-initialization: Apply business rules and validate invariants"""
        self._validate_device_id()
        self._validate_weight()
        self._validate_heart_rate()
        self._classify_heart_rate()
        self._classify_weight()

    def _validate_device_id(self):
        """Business Rule: Device ID must not be empty"""
        if not self.device_id or not self.device_id.strip():
            raise ValueError("Device ID cannot be empty")

    def _validate_weight(self):
        """Business Rule: Weight must be within realistic bounds"""
        if self.weight_kg < 0:
            raise ValueError("Weight cannot be negative")
        if self.weight_kg > 300:
            raise ValueError("Weight exceeds maximum realistic value (300kg)")

    def _validate_heart_rate(self):
        """Business Rule: Heart rate must be within physiological bounds"""
        if self.heart_rate_bpm < 30:
            raise ValueError("Heart rate too low (minimum: 30 BPM)")
        if self.heart_rate_bpm > 220:
            raise ValueError("Heart rate too high (maximum: 220 BPM)")

    def _classify_heart_rate(self):
        """
        Business Logic: Classify heart rate status

        Medical thresholds:
        - Low (Bradycardia): < 60 BPM
        - Normal: 60-100 BPM
        - High (Tachycardia): > 100 BPM
        """
        if self.heart_rate_bpm < 60:
            self.heart_rate_status = HeartRateStatus.LOW
        elif 60 <= self.heart_rate_bpm <= 100:
            self.heart_rate_status = HeartRateStatus.NORMAL
        else:
            self.heart_rate_status = HeartRateStatus.HIGH

    def _classify_weight(self):
        """
        Business Logic: Classify weight alert

        Threshold: > 80 kg triggers overweight alert
        """
        if self.weight_kg > 80:
            self.weight_alert = WeightAlert.OVERWEIGHT
        else:
            self.weight_alert = WeightAlert.NORMAL

    def is_critical(self) -> bool:
        """
        Business Rule: Determine if reading indicates critical condition

        Returns:
            True if heart rate is abnormal or weight is critical
        """
        return (
                self.heart_rate_status in [HeartRateStatus.LOW, HeartRateStatus.HIGH]
                or self.weight_alert == WeightAlert.OVERWEIGHT
        )

    def requires_medical_attention(self) -> bool:
        """
        Business Rule: Determine if reading requires immediate medical attention

        Returns:
            True if heart rate is critically abnormal
        """
        return (
                self.heart_rate_bpm < 40  # Severe bradycardia
                or self.heart_rate_bpm > 120  # Severe tachycardia
        )

    def to_dict(self) -> dict:
        """Convert entity to dictionary representation"""
        return {
            "reading_id": self.reading_id,
            "device_id": self.device_id,
            "weight_kg": self.weight_kg,
            "heart_rate_bpm": self.heart_rate_bpm,
            "heart_rate_status": self.heart_rate_status.value if self.heart_rate_status else None,
            "weight_alert": self.weight_alert.value if self.weight_alert else None,
            "is_critical": self.is_critical(),
            "requires_medical_attention": self.requires_medical_attention(),
            "timestamp": self.timestamp.isoformat(),
            "recorded_at": self.recorded_at.isoformat()
        }


@dataclass
class DeviceStatus:
    """
    Value Object: Device Status

    Represents the current operational status of a device based on
    its most recent vital reading.
    """

    device_id: str
    is_active: bool
    last_reading: Optional[VitalReading]
    last_contact: datetime
    total_readings: int

    def to_dict(self) -> dict:
        """Convert value object to dictionary"""
        return {
            "device_id": self.device_id,
            "is_active": self.is_active,
            "last_contact": self.last_contact.isoformat(),
            "total_readings": self.total_readings,
            "last_reading": self.last_reading.to_dict() if self.last_reading else None
        }