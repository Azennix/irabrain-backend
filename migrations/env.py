from logging.config import fileConfig
import os
from sqlalchemy import text

from sqlalchemy import engine_from_config, pool

from alembic import context
from dotenv import load_dotenv

from database.database import Base
from database.models import (
    MemoryEntity,
    NoteEntity,
    ProjectEntity,
    GoalEntity,
    ProjectTaskEntity,
    ProjectDecisionEntity,
)
from database.conversation.conversation_message_model import ConversationMessageModel
from brain.conversation.conversation_model import ConversationModel
from brain.conversation.conversation_summary_model import (
    ConversationSummaryModel,
)
from database.user_model import User
from database.feedback_model import Feedback
from database.response_feedback_model import ResponseFeedback
from database.notification_model import NotificationEntity
from brain.self_development.persistence.audit_event_model import AuditEventModel
from brain.self_development.persistence.self_development_cycle_model import (
    SelfDevelopmentCycleModel,
)
from brain.self_development.persistence.system_identity_model import (
    SystemIdentityModel,
)

from brain.llm.llm_usage_model import LLMUsage
from brain.recharge.wallet.brain_wallet_model import BrainWalletModel
from brain.recharge.wallet.brain_transaction_model import BrainTransactionModel
from brain.recharge.entitlement.entitlement_model import (
    FreeBrainEntitlementModel,
)

from brain.tier.capacity.capacity_model import (
    TierBrainCapacityModel,
)

from brain.recharge.settlement_model import BrainSettlementModel
from brain.subscription.subscription_model import SubscriptionModel
from brain.payment.payment_model import PaymentModel
# =====================================================
# LOAD ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# ALEMBIC CONFIG
# =====================================================

config = context.config


# =====================================================
# LOGGING
# =====================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# =====================================================
# DATABASE URL
# =====================================================

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set in the environment."
    )

from sqlalchemy.engine import make_url

parsed_url = make_url(database_url)

# Safety guard: never run Alembic against the production database
if parsed_url.database == "irabrain":
    raise RuntimeError(
        "Migration blocked: DATABASE_URL points to 'irabrain'. "
        "Configure the isolated test database 'irabrain_test' first."
    )

print("\n========== ALEMBIC DATABASE DEBUG ==========")
print("DATABASE:", parsed_url.database)
print("HOST:", parsed_url.host)
print("PORT:", parsed_url.port)
print("USERNAME:", parsed_url.username)
print("============================================\n")

config.set_main_option(
    "sqlalchemy.url",
    database_url
)


# =====================================================
# SQLALCHEMY METADATA
# =====================================================

target_metadata = Base.metadata


# =====================================================
# OFFLINE MIGRATIONS
# =====================================================

def run_migrations_offline() -> None:

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()



# =====================================================
# ONLINE MIGRATIONS
# =====================================================

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()



# =====================================================
# RUN
# =====================================================

if context.is_offline_mode():

    run_migrations_offline()

else:

    run_migrations_online()