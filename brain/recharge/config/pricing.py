from dataclasses import dataclass
from decimal import Decimal


# =====================================================
# DEEPSEEK TECHNICAL COST CONFIGURATION
# =====================================================

@dataclass(frozen=True, slots=True)
class DeepSeekCostConfig:
    input_cost_per_million: Decimal
    output_cost_per_million: Decimal
    cached_input_cost_per_million: Decimal
    version: str = "deepseek-v4.1-flash-1"


# =====================================================
# BRAIN UNIT CONFIGURATION
# =====================================================

@dataclass(frozen=True, slots=True)
class BrainUnitConfig:
    unit_cost: Decimal
    currency: str = "INR"
    usd_to_inr_rate: Decimal = Decimal("90")
    version: str = "v2"


# =====================================================
# FREE BRAIN CONFIGURATION
# =====================================================

@dataclass(frozen=True, slots=True)
class FreeBrainConfig:
    allowance: Decimal
    reset_interval_hours: int
    version: str = "v1"


# =====================================================
# COMPLETE BRAIN RECHARGE CONFIGURATION
# =====================================================

@dataclass(frozen=True, slots=True)
class BrainRechargeConfig:
    deepseek: DeepSeekCostConfig
    brain_units: BrainUnitConfig
    free_brain: FreeBrainConfig


# =====================================================
# DEVELOPMENT CONFIGURATION
# =====================================================

DEV_BRAIN_RECHARGE_CONFIG = BrainRechargeConfig(

    deepseek=DeepSeekCostConfig(
        input_cost_per_million=Decimal("0.15"),
        output_cost_per_million=Decimal("0.60"),
        cached_input_cost_per_million=Decimal("0.003"),
    ),

    brain_units=BrainUnitConfig(
        unit_cost=Decimal("0.01"),
        currency="INR",
        usd_to_inr_rate=Decimal("90"),
        version="v2",
),

    free_brain=FreeBrainConfig(
        allowance=Decimal("100"),
        reset_interval_hours=24,
    ),
)