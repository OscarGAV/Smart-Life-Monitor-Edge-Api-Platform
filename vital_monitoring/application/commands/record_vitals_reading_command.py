"""
Application Layer - CQRS Command: Record Vital Reading

This represents a write operation in the CQRS pattern.
Commands change the state of the system.
"""

from dataclasses import dataclass
from vital_monitoring.domain.entities.vitals_reading import VitalReading
from vital_monitoring.domain.repositories.vitals_repository import IVitalRepository


@dataclass
class RecordVitalReadingCommand:
    """
    Command: Record a new vital reading from IoT device

    This command represents the intent to record a new vital parameters
    reading in the system. It encapsulates all the data needed for the operation.

    Attributes:
        device_id: Identifier of the IoT device
        weight_kg: Patient's weight in kilograms
        heart_rate_bpm: Heart rate in beats per minute
    """
    device_id: str
    weight_kg: float
    heart_rate_bpm: int


class RecordVitalReadingCommandHandler:
    """
    Command Handler: Processes RecordVitalReadingCommand

    This handler contains the business logic for recording a vital reading.
    It follows the Command Handler pattern from CQRS.

    Responsibilities:
    - Validate command data
    - Create domain entity
    - Apply business rules
    - Persist through repository
    - Return result
    """

    def __init__(self, repository: IVitalRepository):
        """
        Initialize handler with repository dependency

        Args:
            repository: Implementation of IVitalRepository
        """
        self.repository = repository

    async def handle(self, command: RecordVitalReadingCommand) -> dict:
        """
        Handle the command to record a vital reading

        This method orchestrates the use case:
        1. Create VitalReading entity (applies domain rules)
        2. Persist through repository
        3. Return success result

        Args:
            command: RecordVitalReadingCommand with reading data

        Returns:
            Dictionary with operation result

        Raises:
            ValueError: If domain rules are violated
        """

        # Create domain entity - domain rules are applied in __post_init__
        vital_reading = VitalReading(
            device_id=command.device_id,
            weight_kg=command.weight_kg,
            heart_rate_bpm=command.heart_rate_bpm
        )

        # Persist through repository
        saved_reading = await self.repository.save(vital_reading)

        # Return result
        return {
            "reading_id": saved_reading.reading_id,
            "device_id": saved_reading.device_id,
            "weight_kg": saved_reading.weight_kg,
            "heart_rate_bpm": saved_reading.heart_rate_bpm,
            "heart_rate_status": saved_reading.heart_rate_status.value,
            "weight_alert": saved_reading.weight_alert.value,
            "is_critical": saved_reading.is_critical(),
            "requires_medical_attention": saved_reading.requires_medical_attention(),
            "timestamp": saved_reading.timestamp.isoformat()
        }