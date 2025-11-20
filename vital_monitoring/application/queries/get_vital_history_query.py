"""
Application Layer - CQRS Query: Get Vital History

Retrieves historical vital readings for a device.
"""

from dataclasses import dataclass
from typing import List
from vital_monitoring.domain.repositories.vitals_repository import IVitalRepository


@dataclass
class GetVitalHistoryQuery:
    """
    Query: Get historical vital readings for a device

    Attributes:
        device_id: Identifier of the IoT device
        limit: Maximum number of readings to return
    """
    device_id: str
    limit: int = 50


class GetVitalHistoryQueryHandler:
    """
    Query Handler: Processes GetVitalHistoryQuery

    Retrieves historical data for analysis and monitoring purposes.
    """

    def __init__(self, repository: IVitalRepository):
        """
        Initialize handler with repository dependency

        Args:
            repository: Implementation of IVitalRepository
        """
        self.repository = repository

    async def handle(self, query: GetVitalHistoryQuery) -> List[dict]:
        """
        Handle the query to get vital history

        Args:
            query: GetVitalHistoryQuery with device_id and limit

        Returns:
            List of vital readings as dictionaries
        """

        # Retrieve readings from repository
        readings = await self.repository.find_by_device(
            device_id=query.device_id,
            limit=query.limit
        )

        # Transform to dictionary format
        return [reading.to_dict() for reading in readings]