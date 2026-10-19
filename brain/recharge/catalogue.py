from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class BrainRechargePack:
    pack_id: str
    name: str
    price_inr: Decimal
    units: Decimal
    description: str


BRAIN_RECHARGE_PACKS: dict[str, BrainRechargePack] = {
    "starter": BrainRechargePack(
        pack_id="starter",
        name="STARTER",
        price_inr=Decimal("49.00"),
        units=Decimal("500"),
        description="For everyday AI conversations.",
    ),
    "brain_mini": BrainRechargePack(
        pack_id="brain_mini",
        name="BRAIN MINI",
        price_inr=Decimal("99.00"),
        units=Decimal("1200"),
        description="For regular use and analysis.",
    ),
    "brain_orion": BrainRechargePack(
        pack_id="brain_orion",
        name="BRAIN ORION",
        price_inr=Decimal("199.00"),
        units=Decimal("3000"),
        description="For deeper reasoning and coding.",
    ),
    "thalamus": BrainRechargePack(
        pack_id="thalamus",
        name="THALAMUS",
        price_inr=Decimal("499.00"),
        units=Decimal("9000"),
        description="For advanced tools and demanding work.",
    ),
    "hippocampus": BrainRechargePack(
        pack_id="hippocampus",
        name="HIPPOCAMPUS",
        price_inr=Decimal("999.00"),
        units=Decimal("22000"),
        description="For intensive research and complex tasks.",
    ),
}


def get_recharge_pack(pack_id: str) -> BrainRechargePack:
    pack = BRAIN_RECHARGE_PACKS.get(pack_id)

    if pack is None:
        raise ValueError("Invalid Brain Recharge pack.")

    return pack


def list_recharge_packs() -> tuple[BrainRechargePack, ...]:
    return tuple(BRAIN_RECHARGE_PACKS.values())