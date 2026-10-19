from decimal import Decimal

from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.models import BrainUsageContext, BrainUnitResult
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from brain.recharge.settlement_repository import BrainSettlementRepository


class BrainUsageSettlementService:
    def __init__(
        self,
        cost_resolver: ExecutionCostResolver,
        wallet_operations: BrainWalletOperations,
        included_capacity_service,
        settlement_repository: BrainSettlementRepository,
    ):
        if cost_resolver is None:
            raise ValueError("Cost resolver is required.")

        if wallet_operations is None:
            raise ValueError("Wallet operations are required.")

        if settlement_repository is None:
            raise ValueError("Settlement repository is required.")

        self._cost_resolver = cost_resolver
        self._wallet_operations = wallet_operations

        # Retained for constructor compatibility.
        # Included capacity is no longer a separate spendable balance.
        self._included_capacity_service = included_capacity_service

        self._settlement_repository = settlement_repository

    def settle(
        self,
        context: BrainUsageContext,
        unit_calculator,
    ) -> BrainUnitResult:
        if context is None:
            raise ValueError("Brain usage context is required.")

        if context.user_id is None:
            raise ValueError(
                "User ID is required for Brain Unit settlement."
            )

        if context.user_id == 0:
            return BrainUnitResult(
                units=Decimal("0"),
                calculation_version="guest",
                basis="guest_usage",
                metadata={
                    "reference_id": context.request_id,
                    "settlement": "skipped",
                },
            )

        if context.brain_tier is None:
            raise ValueError(
                "Brain Tier is required for Brain Unit settlement."
            )

        self._settlement_repository.lock_user_settlement(
            context.user_id
        )

        existing_settlement = (
            self._settlement_repository.get_by_request_id(
                context.request_id
            )
        )

        if existing_settlement is not None:
            if existing_settlement["user_id"] != context.user_id:
                raise ValueError(
                    "Settlement reference belongs to a different user."
                )

            return BrainUnitResult(
                units=existing_settlement["total_units"],
                calculation_version=existing_settlement[
                    "calculation_version"
                ],
                basis="idempotent_replay",
                metadata={
                    "reference_id": context.request_id,
                    "free_units": str(
                        existing_settlement["free_units"]
                    ),
                    "paid_units": str(
                        existing_settlement["paid_units"]
                    ),
                },
            )

        execution_cost = self._cost_resolver.resolve(context)

        calculation_context = BrainUsageContext(
            request_id=context.request_id,
            user_id=context.user_id,
            brain_tier=context.brain_tier,
            capability=context.capability,
            task_type=context.task_type,
            provider=context.provider,
            model=context.model,
            input_tokens=context.input_tokens,
            output_tokens=context.output_tokens,
            cached_tokens=context.cached_tokens,
            reasoning_tokens=context.reasoning_tokens,
            total_tokens=context.total_tokens,
            estimated_cost=float(execution_cost.amount),
            tool_usage=context.tool_usage,
            metadata={
                **context.metadata,
                "cost_source": execution_cost.source,
                "cost_version": execution_cost.version,
                "cost_currency": execution_cost.currency,
            },
        )

        result = unit_calculator.calculate(calculation_context)
        units = result.units

        if units <= Decimal("0"):
            raise ValueError(
                "Calculated Brain Units must be greater than zero."
            )

        # Unified wallet:
        # Every billable chat consumes from the same wallet.
        self._wallet_operations.consume(
            user_id=context.user_id,
            units=units,
            reference_id=context.request_id,
            metadata={
                "calculation_version": result.calculation_version,
                "basis": result.basis,
                "provider": context.provider,
                "model": context.model,
                "included_brain_consumed": "0",
            },
        )

        # All usage is wallet-funded; there is no separate free pool.
        self._settlement_repository.create(
            request_id=context.request_id,
            user_id=context.user_id,
            total_units=units,
            free_units=Decimal("0"),
            paid_units=units,
            calculation_version=result.calculation_version,
            basis=result.basis,
            status="completed",
        )

        return result