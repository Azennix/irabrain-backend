from decimal import Decimal
from datetime import datetime, timezone

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


USER_ID = 27

# Current V1 working entitlement values.
# We will centralize these into configuration
# when we finish account provisioning.
FREE_BRAIN_ALLOWANCE = Decimal("100")
RESET_INTERVAL_HOURS = 24


def main():
    session = SessionLocal()

    try:
        service = FreeBrainEntitlementService(
            repository=FreeBrainEntitlementRepository(
                session
            ),
            reset_policy=FreeBrainResetPolicy(),
            consumption_policy=FreeBrainConsumptionPolicy(),
        )

        entitlement = service.get_or_create(
            user_id=USER_ID,
            allowance=FREE_BRAIN_ALLOWANCE,
            reset_interval_hours=RESET_INTERVAL_HOURS,
            now=datetime.now(timezone.utc),
        )

        session.commit()

        print()
        print("======================================")
        print("FREE BRAIN PROVISIONING PASS")
        print("======================================")
        print("User ID       :", entitlement.user_id)
        print("Allowance     :", entitlement.allowance)
        print("Consumed      :", entitlement.consumed)
        print("Reset hours   :", entitlement.reset_interval_hours)
        print("Next reset    :", entitlement.next_reset_at)
        print("======================================")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    main()
