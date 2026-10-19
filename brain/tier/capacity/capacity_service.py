from datetime import datetime, timezone
from decimal import Decimal

from .models import TierBrainCapacity
from .policy import CapacityConsumptionResult
from .repository import TierBrainCapacityRepository
from .service import TierCapacityService


class PersistentTierCapacityService:
    """
    Coordinates persisted tier Brain capacity consumption.

    This layer connects:
    repository -> domain service -> repository.

    It does not contain wallet or settlement logic.
    """

    def __init__(
        self,
        repository: TierBrainCapacityRepository,
        capacity_service: TierCapacityService | None = None,
    ):
        if repository is None:
            raise ValueError(
                "Tier Brain capacity repository is required."
            )

        self._repository = repository
        self._capacity_service = (
            capacity_service or TierCapacityService()
        )

    def consume(
        self,
        user_id: int,
        requested_units: Decimal,
        now: datetime | None = None,
    ) -> tuple[TierBrainCapacity, CapacityConsumptionResult]:

        if user_id <= 0:
            raise ValueError(
                "user_id must be greater than zero."
            )

        capacity = self._repository.get(user_id)

        if capacity is None:
            raise ValueError(
                "Tier Brain capacity does not exist."
            )

        current_time = now or datetime.now(timezone.utc)

        updated_capacity, result = (
            self._capacity_service.consume(
                capacity=capacity,
                requested_units=requested_units,
                now=current_time,
            )
        )

        self._repository.update(
            updated_capacity
        )

        return updated_capacity, result