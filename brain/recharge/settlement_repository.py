import json
from sqlalchemy import text
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from brain.recharge.settlement_model import BrainSettlementModel


class BrainSettlementRepository:
    def __init__(self, session: Session):
        if session is None:
            raise ValueError("Database session is required.")

        self._session = session

    def lock_user_settlement(self, user_id: int) -> None:
        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        self._session.execute(
            text("SELECT pg_advisory_xact_lock(:lock_key)"),
            {"lock_key": user_id},
)

    def get_by_request_id(
        self,
        request_id: str,
    ) -> dict | None:
        if not request_id:
            raise ValueError("Request ID is required.")

        model = (
            self._session.query(BrainSettlementModel)
            .filter(
                BrainSettlementModel.request_id == request_id
            )
            .first()
        )

        if model is None:
            return None

        return {
            "request_id": model.request_id,
            "user_id": model.user_id,
            "total_units": Decimal(model.total_units),
            "free_units": Decimal(model.free_units),
            "paid_units": Decimal(model.paid_units),
            "calculation_version": model.calculation_version,
            "basis": model.basis,
            "status": model.status,
            "created_at": model.created_at,
        }

    def create(
        self,
        request_id: str,
        user_id: int,
        total_units: Decimal,
        free_units: Decimal,
        paid_units: Decimal,
        calculation_version: str,
        basis: str,
        status: str,
    ) -> dict:
        if not request_id:
            raise ValueError("Request ID is required.")

        if user_id <= 0:
            raise ValueError("User ID must be greater than zero.")

        if total_units <= Decimal("0"):
            raise ValueError(
                "Total Brain Units must be greater than zero."
            )

        if free_units < Decimal("0"):
            raise ValueError(
                "Free Brain Units cannot be negative."
            )

        if paid_units < Decimal("0"):
            raise ValueError(
                "Paid Brain Units cannot be negative."
            )

        if free_units + paid_units != total_units:
            raise ValueError(
                "Free and paid Brain Units must equal total Brain Units."
            )

        if not calculation_version:
            raise ValueError(
                "Calculation version is required."
            )

        if not basis:
            raise ValueError("Settlement basis is required.")

        if not status:
            raise ValueError("Settlement status is required.")

        model = BrainSettlementModel(
            request_id=request_id,
            user_id=user_id,
            total_units=total_units,
            free_units=free_units,
            paid_units=paid_units,
            calculation_version=calculation_version,
            basis=basis,
            status=status,
            created_at=datetime.now(timezone.utc),
        )

        self._session.add(model)
        self._session.flush()

        return {
            "request_id": model.request_id,
            "user_id": model.user_id,
            "total_units": Decimal(model.total_units),
            "free_units": Decimal(model.free_units),
            "paid_units": Decimal(model.paid_units),
            "calculation_version": model.calculation_version,
            "basis": model.basis,
            "status": model.status,
            "created_at": model.created_at,
        }