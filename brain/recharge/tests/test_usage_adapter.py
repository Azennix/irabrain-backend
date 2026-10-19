from decimal import Decimal
from datetime import datetime, timezone
from brain.llm.usage import LLMUsageRecord
from brain.recharge.calculator import (
    BrainUnitCalculator,
    CostBasedBrainUnitPolicy,
)
from brain.recharge.cost.cost_resolver import ExecutionCostResolver
from brain.recharge.cost.passthrough_cost_source import (
    PassthroughExecutionCostSource,
)
from brain.recharge.settlement import BrainUsageSettlementService
from brain.recharge.usage_adapter import LLMUsageToBrainUsageAdapter
from brain.recharge.wallet.repository import BrainWalletRepository
from brain.recharge.wallet.service import BrainWalletService
from brain.recharge.wallet.transaction_repository import (
    BrainTransactionRepository,
)
from brain.recharge.wallet.wallet_operations import BrainWalletOperations
from database.database import SessionLocal
from brain.recharge.entitlement.repository import (
    FreeBrainEntitlementRepository,
)
from brain.recharge.entitlement.reset_policy import (
    FreeBrainResetPolicy,
)
from brain.recharge.entitlement.consumption import (
    FreeBrainConsumptionPolicy,
)
from brain.recharge.entitlement.service import (
    FreeBrainEntitlementService,
)
from brain.recharge.settlement_repository import (
    BrainSettlementRepository,
)
from brain.recharge.included_capacity_service import (
    IncludedBrainCapacityService,
)
from brain.tier.capacity.repository import TierBrainCapacityRepository
from brain.tier.capacity.capacity_service import PersistentTierCapacityService
from brain.recharge.included_capacity_service import IncludedBrainCapacityService
from brain.tier.models import BrainTier
def test_llm_usage_is_settled_into_brain_units():
    session = SessionLocal()

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        user_id = 999987

        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("100"),
            reference_id="usage-adapter-recharge-001",
        )

        cost_resolver = ExecutionCostResolver(
            sources=[
                PassthroughExecutionCostSource(),
            ]
        )

        free_brain_service = FreeBrainEntitlementService(
            repository=FreeBrainEntitlementRepository(session),
            reset_policy=FreeBrainResetPolicy(),
            consumption_policy=FreeBrainConsumptionPolicy(),
)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("1"),
            reset_interval_hours=24,
            now=datetime.now(timezone.utc),
)


        settlement_repository = BrainSettlementRepository(session)
        tier_capacity_service = PersistentTierCapacityService(
            repository=TierBrainCapacityRepository(session),
)
        included_capacity_service = IncludedBrainCapacityService(
            free_brain_service=free_brain_service,
            tier_capacity_service=tier_capacity_service,

)

        settlement_service = BrainUsageSettlementService(
            cost_resolver=cost_resolver,
            wallet_operations=wallet_operations,
            included_capacity_service=included_capacity_service,
            settlement_repository=settlement_repository,
)

        unit_calculator = BrainUnitCalculator(
            policy=CostBasedBrainUnitPolicy(
                unit_cost=Decimal("0.01"),
                version="v1",
            )
        )

        adapter = LLMUsageToBrainUsageAdapter(
            settlement_service=settlement_service,
            unit_calculator=unit_calculator,
        )

        usage = LLMUsageRecord(
            request_id="usage-adapter-test-001",
            user_id=str(user_id),
            provider="ollama",
            model="qwen2.5:7b",
            brain_tier=BrainTier.FREE,
            input_tokens=100,
            output_tokens=20,
            total_tokens=120,
            estimated_cost=0.05,
            latency=1.2,
            success=True,
        )

        result = adapter.settle(usage)

        assert result.units == 5.0
        assert result.calculation_version == "v1"
        assert result.basis == "execution_cost"

        wallet = wallet_repository.get(user_id)

        assert wallet is not None
        assert wallet.current_balance == Decimal("96")
        assert wallet.lifetime_purchased == Decimal("100")
        assert wallet.lifetime_consumed == Decimal("4")

        transaction = transaction_repository.get_by_reference_id(
            "usage-adapter-test-001"
        )

        assert transaction is not None
        assert transaction.user_id == user_id
        assert transaction.units == Decimal("4")

        session.rollback()

    finally:
        session.close()