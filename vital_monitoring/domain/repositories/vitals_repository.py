"""
Domain Layer - Repository Interface
Bounded Context: Vital Monitoring

This defines the contract for persistence operations without
specifying the implementation (DDD Repository Pattern).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from vital_monitoring.domain.entities.vitals_reading import VitalReading


class IVitalRepository(ABC):
    """
    Repository Interface for VitalReading Aggregate

    This interface defines the contract for persistence operations
    following the Repository pattern from Domain-Driven Design.
    The actual implementation is in the Infrastructure layer.
    """

    @abstractmethod
    async def save(self, vital_reading: VitalReading) -> VitalReading:
        """
        Persist a vital reading

        Args:
            vital_reading: The VitalReading entity to save

        Returns:
            The saved VitalReading entity
        """
        pass

    @abstractmethod
    async def find_by_id(self, reading_id: str) -> Optional[VitalReading]:
        """
        Find a vital reading by its unique identifier

        Args:
            reading_id: Unique identifier of the reading

        Returns:
            VitalReading if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_device(
            self,
            device_id: str,
            limit: int = 50
    ) -> List[VitalReading]:
        """
        Find all vital readings for a specific device

        Args:
            device_id: Identifier of the IoT device
            limit: Maximum number of readings to return

        Returns:
            List of VitalReading entities, ordered by timestamp (most recent first)
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def count_by_device(self, device_id: str) -> int:
        """
        Count total readings for a device

        Args:
            device_id: Identifier of the IoT device

        Returns:
            Total number of readings
        """
        pass

    @abstractmethod
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
        pass