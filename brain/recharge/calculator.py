from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_UP

from brain.recharge.models import (
    BrainUnitResult,
    BrainUsageContext,
)


class BrainUnitCalculationPolicy(ABC):
    """
    Defines how Brain Units are calculated.

    The policy is separated from the calculator so that
    IRABRAIN's usage economics can evolve independently.
    """

    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def calculate(
        self,
        context: BrainUsageContext,
    ) -> BrainUnitResult:
        raise NotImplementedError


class CostBasedBrainUnitPolicy(BrainUnitCalculationPolicy):
    """
    Converts an execution cost into normalized Brain Units.

    Economic values are injected into the policy.
    Nothing is hardcoded into the calculation itself.
    """

    def __init__(
        self,
        unit_cost: Decimal,
        version: str,
        target_currency: str = "USD",
        usd_to_inr_rate: Decimal = Decimal("90"),
    ):
        if unit_cost <= Decimal("0"):
            raise ValueError("Brain Unit cost must be greater than zero.")

        if not version.strip():
            raise ValueError("Brain Unit calculation version is required.")

        self._unit_cost = unit_cost
        self._version = version

        self._target_currency = target_currency.upper()
        self._usd_to_inr_rate = usd_to_inr_rate

        if self._target_currency not in {"USD", "INR"}:
            raise ValueError("Unsupported Brain Unit currency.")

        if self._usd_to_inr_rate <= Decimal("0"):
            raise ValueError("USD to INR exchange rate must be positive.")


    @property
    def version(self) -> str:
        return self._version

    def calculate(
        self,
        context: BrainUsageContext,
    ) -> BrainUnitResult:
        if context.estimated_cost is None:
            raise ValueError(
                "A technical execution cost is required "
                "for cost-based Brain Unit calculation."
            )

        cost = Decimal(str(context.estimated_cost))

        source_currency = str(
            context.metadata.get("cost_currency", self._target_currency)
        ).upper()

        if source_currency != self._target_currency:
            if source_currency == "USD" and self._target_currency == "INR":
                cost *= self._usd_to_inr_rate
            else:
               raise ValueError(
                    f"Unsupported currency conversion: "
                    f"{source_currency} -> {self._target_currency}"
        )

        if cost < Decimal("0"):
            raise ValueError("Execution cost cannot be negative.")

        units = (
            cost / self._unit_cost
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_UP,
        )

        return BrainUnitResult(
            units=units,
            calculation_version=self.version,
            basis="execution_cost",
            metadata={
                **context.metadata,
                "provider": context.provider,
                "model": context.model,
            },
        )


class BrainUnitCalculator:
    """
    Application-facing Brain Unit calculation boundary.

    This component does not know about payments, wallets,
    Razorpay, databases, or frontend concerns.
    """

    def __init__(self, policy: BrainUnitCalculationPolicy):
        if policy is None:
            raise ValueError(
                "Brain Unit calculation policy is required."
            )

        self._policy = policy

    def calculate(
        self,
        context: BrainUsageContext,
    ) -> BrainUnitResult:
        if context is None:
            raise ValueError(
                "Brain usage context is required."
            )

        if not context.request_id:
            raise ValueError(
                "Brain usage context requires a request_id."
            )

        return self._policy.calculate(context)