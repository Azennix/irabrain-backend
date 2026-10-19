from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from brain.self_development.persistence.self_development_cycle_model import (
    SelfDevelopmentCycleModel,
)


class SelfDevelopmentCycleRepository:

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # FIND CYCLE
    # =====================================================

    def get_by_id(
        self,
        cycle_id: str,
    ) -> Optional[SelfDevelopmentCycleModel]:

        return (
            self.db.query(
                SelfDevelopmentCycleModel
            )
            .filter(
                SelfDevelopmentCycleModel.cycle_id
                == cycle_id
            )
            .first()
        )

    # =====================================================
    # CREATE CYCLE
    # =====================================================

    def create(
        self,
        cycle_id: str,
        user_id: int,
        improvement_id: str,
        stage: str,
        context: Optional[Dict[str, Any]] = None,
        system_id: Optional[str] = None,
    ) -> SelfDevelopmentCycleModel:

        if user_id is None and system_id is None:
            raise ValueError(
                "Either user_id or system_id is required."
        )

        if user_id is not None and system_id is not None:
            raise ValueError(
                "A cycle cannot belong to both a human and a system."
        )

        cycle = SelfDevelopmentCycleModel(
            cycle_id=cycle_id,
            user_id=user_id,
            system_id=system_id,
            improvement_id=improvement_id,
            stage=stage,
            context=context or {},
        )

        self.db.add(cycle)
        self.db.flush()

        return cycle

    # =====================================================
    # SAVE CYCLE
    # =====================================================

    def save(
        self,
        cycle: SelfDevelopmentCycleModel,
    ) -> SelfDevelopmentCycleModel:

        self.db.add(cycle)
        self.db.flush()

        return cycle

    # =====================================================
    # UPDATE STAGE
    # =====================================================

    def update_stage(
        self,
        cycle_id: str,
        stage: str,
    ) -> Optional[SelfDevelopmentCycleModel]:

        cycle = self.get_by_id(cycle_id)

        if cycle is None:
            return None

        cycle.stage = stage

        self.db.flush()

        return cycle

    # =====================================================
    # UPDATE CONTEXT
    # =====================================================

    def update_context(
        self,
        cycle_id: str,
        context: Dict[str, Any],
    ) -> Optional[SelfDevelopmentCycleModel]:

        cycle = self.get_by_id(cycle_id)

        if cycle is None:
            return None

        cycle.context = dict(context)

        self.db.flush()

        return cycle

    # =====================================================
    # UPDATE RESULT
    # =====================================================

    def update_result(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]],
    ) -> Optional[SelfDevelopmentCycleModel]:

        cycle = self.get_by_id(cycle_id)

        if cycle is None:
            return None

        cycle.result = (
            dict(result)
            if result is not None
            else None
        )

        self.db.flush()

        return cycle

    # =====================================================
    # UPDATE ERROR
    # =====================================================

    def update_error(
        self,
        cycle_id: str,
        error: Optional[str],
    ) -> Optional[SelfDevelopmentCycleModel]:

        cycle = self.get_by_id(cycle_id)

        if cycle is None:
            return None

        cycle.error = error

        self.db.flush()

        return cycle

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self) -> None:

        self.db.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self) -> None:

        self.db.rollback()