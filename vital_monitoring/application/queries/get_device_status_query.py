"""
Application Layer - CQRS Query: Get Device Status

This represents a read operation in the CQRS pattern.
Queries retrieve data without modifying system state.
"""

from dataclasses import dataclass
from typing import Optional

from vital_monitoring.domain.repositories.vitals_repository import IVitalRepository


@dataclass
class GetDeviceStatusQuery:
    """
    Query: Get current status of an IoT device

    This query retrieves the current operational status and
    most recent vital reading for a specific device.

    Attributes:
        device_id: Identifier of the IoT device
    """
    device_id: str


class GetDeviceStatusQueryHandler:
    """
    Query Handler: Processes GetDeviceStatusQuery

    This handler retrieves device status information without
    modifying any data. It follows the Query Handler pattern from CQRS.

    Responsibilities:
    - Validate query parameters
    - Retrieve data from repository
    - Transform to appropriate response format
    - Return read-only data
    """

    def __init__(self, repository: IVitalRepository):
        """
        Initialize handler with repository dependency

        Args:
            repository: Implementation of IVitalRepository
        """
        self.repository = repository

    async def handle(self, query: GetDeviceStatusQuery) -> Optional[dict]:
        """
        Handle the query to get device status

        This method:
        1. Retrieves latest reading for the device
        2. Gets total readings count
        3. Constructs status response

        Args:
            query: GetDeviceStatusQuery with device_id

        Returns:
            Dictionary with device status or None if device not found
        """

        # Get latest reading
        latest_reading = await self.repository.find_latest_by_device(
            query.device_id
        )

        if not latest_reading:
            return None

        # Get total readings count
        total_readings = await self.repository.count_by_device(query.device_id)

        # Construct response
        return {
            "device_id": query.device_id,
            "is_active": True,
            "last_contact": latest_reading.timestamp.isoformat(),
            "total_readings": total_readings,
            "current_status": {
                "weight_kg": latest_reading.weight_kg,
                "heart_rate_bpm": latest_reading.heart_rate_bpm,
                "heart_rate_status": latest_reading.heart_rate_status.value,
                "weight_alert": latest_reading.weight_alert.value,
                "is_critical": latest_reading.is_critical(),
                "requires_medical_attention": latest_reading.requires_medical_attention()
            },
            "latest_reading": latest_reading.to_dict()
        }