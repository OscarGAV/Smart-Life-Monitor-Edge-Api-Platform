"""
Infrastructure Layer - In-Memory Repository Implementation

This is a concrete implementation of IVitalRepository using
in-memory storage. In production, this would be replaced with
a database implementation (PostgreSQL, MongoDB, etc.).
"""

from typing import List, Optional, Dict

from vital_monitoring.domain.entities.vitals_reading import VitalReading
from vital_monitoring.domain.repositories.vitals_repository import IVitalRepository


class InMemoryVitalRepository(IVitalRepository):
    """
    In-Memory implementation of VitalRepository

    This implementation stores data in memory using dictionaries.
    Suitable for development, testing, and edge scenarios with
    limited connectivity.

    Storage structure:
    - _readings: Dict[reading_id, VitalReading]
    - _device_readings: Dict[device_id, List[reading_id]]
    """

    def __init__(self):
        """Initialize in-memory storage"""
        self._readings: Dict[str, VitalReading] = {}
        self._device_readings: Dict[str, List[str]] = {}
        print("📦 InMemoryVitalRepository initialized")

    async def save(self, vital_reading: VitalReading) -> VitalReading:
        """
        Save a vital reading to memory

        Args:
            vital_reading: The VitalReading entity to save

        Returns:
            The saved VitalReading entity
        """
        # Store reading
        self._readings[vital_reading.reading_id] = vital_reading

        # Index by device
        if vital_reading.device_id not in self._device_readings:
            self._device_readings[vital_reading.device_id] = []

        self._device_readings[vital_reading.device_id].append(
            vital_reading.reading_id
        )

        print(f"✅ Saved reading {vital_reading.reading_id} for device {vital_reading.device_id}")

        return vital_reading

    async def find_by_id(self, reading_id: str) -> Optional[VitalReading]:
        """
        Find a vital reading by ID

        Args:
            reading_id: Unique identifier of the reading

        Returns:
            VitalReading if found, None otherwise
        """
        return self._readings.get(reading_id)

    async def find_by_device(
            self,
            device_id: str,
            limit: int = 50
    ) -> List[VitalReading]:
        """
        Find all vital readings for a device

        Args:
            device_id: Identifier of the IoT device
            limit: Maximum number of readings to return

        Returns:
            List of VitalReading entities, ordered by timestamp (most recent first)
        """
        if device_id not in self._device_readings:
            return []

        # Get reading IDs for device
        reading_ids = self._device_readings[device_id]

        # Get actual readings
        readings = [
            self._readings[rid]
            for rid in reading_ids
            if rid in self._readings
        ]

        # Sort by timestamp (most recent first)
        readings.sort(key=lambda r: r.timestamp, reverse=True)

        # Apply limit
        return readings[:limit]

    async def find_latest_by_device(
            self,
            device_id: str
    ) -> Optional[VitalReading]:
        """
        Find the most recent vital reading for a device

        Args:
            device_id: Identifier of the IoT device

        Returns:
            Most recent VitalReading if found, None otherwise
        """
        readings = await self.find_by_device(device_id, limit=1)
        return readings[0] if readings else None

    async def count_by_device(self, device_id: str) -> int:
        """
        Count total readings for a device

        Args:
            device_id: Identifier of the IoT device

        Returns:
            Total number of readings
        """
        if device_id not in self._device_readings:
            return 0
        return len(self._device_readings[device_id])

    async def find_critical_readings(
            self,
            device_id: Optional[str] = None
    ) -> List[VitalReading]:
        """
        Find all critical vital readings

        Args:
            device_id: Optional device filter

        Returns:
            List of critical VitalReading entities
        """
        if device_id:
            readings = await self.find_by_device(device_id, limit=1000)
        else:
            readings = list(self._readings.values())

        # Filter critical readings
        critical = [r for r in readings if r.is_critical()]

        # Sort by timestamp (most recent first)
        critical.sort(key=lambda r: r.timestamp, reverse=True)

        return critical

    def get_statistics(self) -> dict:
        """
        Get repository statistics (useful for monitoring)

        Returns:
            Dictionary with storage statistics
        """
        return {
            "total_readings": len(self._readings),
            "total_devices": len(self._device_readings),
            "devices": {
                device_id: len(reading_ids)
                for device_id, reading_ids in self._device_readings.items()
            }
        }