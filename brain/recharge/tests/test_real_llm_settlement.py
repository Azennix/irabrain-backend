from decimal import Decimal
from datetime import datetime, timezone
from brain.base.brain_request import BrainRequest
from brain.orchestrator.brain_orchestrator import BrainOrchestrator
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
from brain.recharge.settlement_model import BrainSettlementModel
from database.user_model import User
from brain.tier.models import BrainTier

def test_real_llm_usage_settles_brain_units():
    session = SessionLocal()

    user_id = 999985

    user = session.query(User).filter(
        User.user_id == user_id
    ).first()

    if user is None:
        user = User(
            user_id=user_id,
           email="real-llm-settlement-test@example.com",
            full_name="Real LLM Settlement Test",
            email_verified=True,
            is_active=True,
            brain_tier=BrainTier.FREE.value,
    )
        session.add(user)
        session.flush()
    else:
        user.brain_tier = BrainTier.FREE.value

    try:
        wallet_repository = BrainWalletRepository(session)
        transaction_repository = BrainTransactionRepository(session)
        wallet_service = BrainWalletService()

        wallet_operations = BrainWalletOperations(
            wallet_repository=wallet_repository,
            transaction_repository=transaction_repository,
            wallet_service=wallet_service,
        )

        free_brain_service = FreeBrainEntitlementService(
            repository=FreeBrainEntitlementRepository(session),
            reset_policy=FreeBrainResetPolicy(),
            consumption_policy=FreeBrainConsumptionPolicy(),
)

        free_brain_service.get_or_create(
            user_id=user_id,
            allowance=Decimal("500"),
            reset_interval_hours=24,
            now=datetime.now(timezone.utc),
)

        # Give the test user enough Brain Balance.
        wallet_operations.recharge(
            user_id=user_id,
            units=Decimal("10000"),
            reference_id="real-llm-settlement-recharge-001",
            metadata={
                "source": "real_llm_settlement_test",
            },
        )

        orchestrator = BrainOrchestrator(session)

        request = BrainRequest(
            user_id=user_id,
            query="Reply with exactly one short sentence: What is 2 + 2?",
            metadata={
                "workspace_mode": "personal",
            },
        )

        response = orchestrator.process(request)

        assert response
        assert isinstance(response, str)

        wallet = wallet_repository.get(user_id)

        assert wallet is not None

        assert wallet.current_balance < Decimal("10000")
        assert wallet.lifetime_consumed > Decimal("0")

        usage = (
            session.query(
                __import__(
                    "brain.llm.llm_usage_model",
                    fromlist=["LLMUsage"],
                ).LLMUsage
            )
            .filter(
                __import__(
                    "brain.llm.llm_usage_model",
                    fromlist=["LLMUsage"],
                ).LLMUsage.request_id
                == request.request_id
            )
            .first()
        )

        assert usage is not None
        assert usage.provider == "deepseek"
        assert usage.model == "deepseek-flash"
        assert usage.success is True
        assert usage.input_tokens is not None
        assert usage.output_tokens is not None
        assert usage.total_tokens is not None

        settlement = (
            session.query(BrainSettlementModel)
            .filter(
                BrainSettlementModel.request_id
                == request.request_id
    )
            .first()
)

        assert settlement is not None
        assert settlement.user_id == user_id
        assert settlement.total_units > Decimal("0")
        assert settlement.free_units >= Decimal("0")
        assert settlement.paid_units >= Decimal("0")
        assert settlement.status == "completed"

        print("\nREAL LLM SETTLEMENT: PASS")
        print("Response:", response)
        print("Input tokens:", usage.input_tokens)
        print("Output tokens:", usage.output_tokens)
        print("Total tokens:", usage.total_tokens)
        print("Brain Units consumed:", settlement.total_units)
        print("Free Brain consumed:", settlement.free_units)
        print("Paid Brain consumed:", settlement.paid_units)
        print("Remaining Brain Balance:", wallet.current_balance)
        orchestrator.close()

        session.rollback()

    finally:
        session.close()