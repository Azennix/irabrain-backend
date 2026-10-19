from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from brain.self_development.persistence.self_development_cycle_repository import (
    SelfDevelopmentCycleRepository,
)
from brain.self_development.persistence.system_identity_repository import (
    SystemIdentityRepository,
)
from brain.self_development.security.system_authorization_policy import (
    SystemAuthorizationPolicy,
)
from brain.self_development.audit.audit_service import AuditService



class SelfDevelopmentStage(str, Enum):
    """
    Represents the current stage of a self-development cycle.
    """

    CREATED = "created"
    OBSERVATION = "observation"
    INVESTIGATION = "investigation"
    PLANNING = "planning"
    DEVELOPMENT = "development"
    LINTING = "linting"
    TESTING = "testing"
    BUILD = "build"
    EVALUATION = "evaluation"
    STAGING = "staging"
    CANARY = "canary"
    RELEASE = "release"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class SelfDevelopmentCycle:
    """
    Represents one controlled self-development cycle.
    """

    cycle_id: str
    improvement_id: str

    stage: SelfDevelopmentStage = (
        SelfDevelopmentStage.CREATED
    )

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    result: Optional[Dict[str, Any]] = None

    error: Optional[str] = None

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = field(
        default_factory=datetime.utcnow
    )


class SelfDevelopmentOrchestrator:
    """
    Coordinates the IRABRAIN self-development pipeline.

    This component is the coordinator for the
    self-development subsystem.

    It does NOT:
    - directly modify production source code
    - bypass capability policy
    - bypass change policy
    - bypass release policy
    - independently authorize production release
    - replace the main Brain Orchestrator

    The main Brain Orchestrator may invoke this
    component when a self-development operation
    is required.
    """

    def __init__(
        self,
        capability_policy=None,
        change_policy=None,
        release_policy=None,
        cycle_repository: Optional[
            SelfDevelopmentCycleRepository
    ] = None,
        system_identity_repository: Optional[
            SystemIdentityRepository
    ] = None,
        system_authorization_policy: Optional[
            SystemAuthorizationPolicy
    ] = None,
    audit_service: Optional[AuditService] = None,

    ):
        self.capability_policy = capability_policy
        self.change_policy = change_policy
        self.release_policy = release_policy
        self.cycle_repository = cycle_repository
        self.system_identity_repository = (
            system_identity_repository
    )
        self.system_authorization_policy = (
            system_authorization_policy
)
        self.audit_service = audit_service

        self._cycles: Dict[
            str,
            SelfDevelopmentCycle,
        ] = {}

        self._counter = 0

    def create_cycle(
        self,
        improvement_id: str,
        user_id: Optional[int] = None,
        system_id: Optional[str] = None,
    ) -> SelfDevelopmentCycle:

        if not improvement_id.strip():
            raise ValueError(
                "Improvement ID cannot be empty."
            )
          # -------------------------------------------------
    # OWNERSHIP VALIDATION
    # -------------------------------------------------

        if user_id is None and system_id is None:
            raise ValueError(
                "Either user_id or system_id is required."
        )

        if user_id is not None and system_id is not None:
            raise ValueError(
                "A cycle cannot belong to both a human and a system."
        )
         # -------------------------------------------------
    # SYSTEM IDENTITY VALIDATION
    # -------------------------------------------------

        if system_id is not None:

            if not system_id.strip():
                raise ValueError(
                    "System ID cannot be empty."
        )

            if self.system_identity_repository is None:
                raise ValueError(
                    "System identity repository is required "
                    "for system-owned cycles."
        )

            system_identity = (
                self.system_identity_repository.get_by_id(
                    system_id
        )
    )

            if system_identity is None:
                raise ValueError(
                    f"Unknown system identity: {system_id}"
        )

            if not system_identity.is_active:
                raise ValueError(
                    f"System identity is inactive: {system_id}"
        )


            authorization = (
                self.system_authorization_policy
                if self.system_authorization_policy is not None
                else SystemAuthorizationPolicy()
)

            decision = authorization.authorize("observation")

            if not decision.allowed:
               raise PermissionError(
                decision.reason
    )
            # -------------------------------------------------
    # CREATE CYCLE
    # -------------------------------------------------


        cycle_id = self._next_cycle_id()

        cycle = SelfDevelopmentCycle(
            cycle_id=cycle_id,
            improvement_id=improvement_id,
        )

        self._cycles[cycle_id] = cycle

          # -------------------------------------------------
    # PERSIST
    # -------------------------------------------------

        if self.cycle_repository is not None:

            self.cycle_repository.create(
                cycle_id=cycle.cycle_id,
                user_id=user_id,
                system_id=system_id,
                improvement_id=cycle.improvement_id,
                stage=cycle.stage.value,
                context=cycle.context,
        )

            self.cycle_repository.commit()



        if self.audit_service is not None:
            self.audit_service.record(
                cycle_id=cycle.cycle_id,
                system_id=system_id,
                user_id=user_id,
                event_type="cycle_created",
                action="cycle_creation",
                stage=cycle.stage,
                outcome="success",
                details={
                    "improvement_id": improvement_id,
        },
    )



        return cycle

    def _next_cycle_id(self) -> str:
        if self.cycle_repository is None:
            self._counter += 1
            return f"SDC-{self._counter:04d}"

        while True:
            self._counter += 1
            cycle_id = f"SDC-{self._counter:04d}"

            existing = self.cycle_repository.get_by_id(
                cycle_id
        )

            if existing is None:
                return cycle_id



    def _get(self, cycle_id: str) -> SelfDevelopmentCycle:
        try:
            return self._cycles[cycle_id]
        except KeyError:
            pass

        if self.cycle_repository is not None:
            persisted_cycle = self.cycle_repository.get_by_id(cycle_id)

            if persisted_cycle is not None:
                cycle = SelfDevelopmentCycle(
                    cycle_id=persisted_cycle.cycle_id,
                    improvement_id=persisted_cycle.improvement_id,
                    stage=SelfDevelopmentStage(persisted_cycle.stage),
                    context=dict(persisted_cycle.context or {}),
                    result=persisted_cycle.result,
                    error=persisted_cycle.error,
                    created_at=persisted_cycle.created_at,
                    updated_at=persisted_cycle.updated_at,
            )

                self._cycles[cycle_id] = cycle
                return cycle

        raise KeyError(
            f"Unknown self-development cycle: {cycle_id}"
    )

    def advance(
        self,
        cycle_id: str,
        stage: SelfDevelopmentStage,
        context: Optional[Dict[str, Any]] = None,
    ) -> SelfDevelopmentCycle:

        cycle = self._get(cycle_id)

        if not isinstance(
            stage,
            SelfDevelopmentStage,
        ):
            raise ValueError(
                "Invalid self-development stage."
            )
        previous_stage = cycle.stage

        cycle.stage = stage

        if context is not None:
            cycle.context.update(context)

        cycle.updated_at = datetime.utcnow()

        if self.cycle_repository is not None:
            self.cycle_repository.update_stage(
                cycle.cycle_id,
                cycle.stage.value,
    )

            self.cycle_repository.update_context(
                cycle.cycle_id,
                cycle.context,
    )

            self.cycle_repository.commit()

        if self.audit_service is not None:
            system_id = None
            user_id = None
            if self.cycle_repository is not None:
                stored_cycle = self.cycle_repository.get_by_id(
                cycle.cycle_id        )

                if stored_cycle is not None:
                    system_id = stored_cycle.system_id
                    user_id = stored_cycle.user_id

            self.audit_service.record(
                cycle_id=cycle.cycle_id,
                system_id=system_id,
                user_id=user_id,
                event_type="stage_transition",
                action="stage_transition",
                stage=stage.value,
                     outcome="success",
                     details={
                      "from_stage": previous_stage.value,
                      "to_stage": stage.value,
        },
    )

        return cycle

    def complete(
        self,
        cycle_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> SelfDevelopmentCycle:

        cycle = self._get(cycle_id)

        cycle.stage = (
            SelfDevelopmentStage.COMPLETED
        )

        cycle.result = (
            dict(result)
            if result is not None
            else {}
        )

        cycle.updated_at = datetime.utcnow()

        return cycle

    def fail(
        self,
        cycle_id: str,
        error: str,
    ) -> SelfDevelopmentCycle:

        cycle = self._get(cycle_id)

        if not error.strip():
            raise ValueError(
                "Failure reason cannot be empty."
            )
        previous_stage = cycle.stage

        cycle.stage = (
            SelfDevelopmentStage.FAILED
        )

        cycle.error = error

        cycle.updated_at = datetime.utcnow()
        if self.cycle_repository is not None:
            self.cycle_repository.update_stage(
            cycle.cycle_id,
            cycle.stage.value,
        )
            self.cycle_repository.commit()


        if self.audit_service is not None:
            system_id = None
            user_id = None

            if self.cycle_repository is not None:
                stored_cycle = self.cycle_repository.get_by_id(
                    cycle.cycle_id
        )
                if stored_cycle is not None:
                    system_id = stored_cycle.system_id
                    user_id = stored_cycle.user_id


            self.audit_service.record(
                cycle_id=cycle.cycle_id,
                system_id=system_id,
                user_id=user_id,
                event_type="cycle_failed",
                action="failure",
                stage=cycle.stage.value,
                outcome="failure",
                details={
                    "from_stage": previous_stage.value,
                    "to_stage": cycle.stage.value,
                    "error": error,
            },
        )

        return cycle

    def rollback(
        self,
        cycle_id: str,
        reason: str,
    ) -> SelfDevelopmentCycle:

        cycle = self._get(cycle_id)

        if not reason.strip():
            raise ValueError(
                "Rollback reason cannot be empty."
            )
        previous_stage = cycle.stage

        cycle.stage = (
            SelfDevelopmentStage.ROLLED_BACK
        )

        cycle.error = reason

        cycle.updated_at = datetime.utcnow()


        if self.cycle_repository is not None:
            self.cycle_repository.update_stage(
                 cycle.cycle_id,
                cycle.stage.value,
        )

            self.cycle_repository.commit()



        if self.audit_service is not None:
            system_id = None
            user_id = None

            if self.cycle_repository is not None:
                stored_cycle = self.cycle_repository.get_by_id(
                    cycle.cycle_id
        )
                if stored_cycle is not None:
                    system_id = stored_cycle.system_id
                    user_id = stored_cycle.user_id

            self.audit_service.record(
                cycle_id=cycle.cycle_id,
                system_id=system_id,
                user_id=user_id,
                event_type="cycle_rolled_back",
                action="rollback",
                stage=cycle.stage.value,
                outcome="success",
                details={
                    "from_stage": previous_stage.value,
                    "to_stage": cycle.stage.value,
                    "reason": reason,
            },
        )

        return cycle

    def history(self):
        return list(
            self._cycles.values()
        )
    def get(self, cycle_id: str) -> SelfDevelopmentCycle:
        """
        Get a self-development cycle.

        The cycle is loaded from memory when available,
        otherwise recovered from persistent storage.
        """
        return self._get(cycle_id)

    def _get(self, cycle_id: str) -> SelfDevelopmentCycle:
        if cycle_id in self._cycles:
            return self._cycles[cycle_id]

        if self.cycle_repository is not None:
            persisted_cycle = self.cycle_repository.get_by_id(cycle_id)

            if persisted_cycle is not None:
                cycle = SelfDevelopmentCycle(
                    cycle_id=persisted_cycle.cycle_id,
                    improvement_id=persisted_cycle.improvement_id,
                    stage=SelfDevelopmentStage(persisted_cycle.stage),
                    context=dict(persisted_cycle.context or {}),
                    result=persisted_cycle.result,
                    error=persisted_cycle.error,
                    created_at=persisted_cycle.created_at,
                    updated_at=persisted_cycle.updated_at,
            )

                self._cycles[cycle_id] = cycle
                return cycle

        raise KeyError(
            f"Unknown self-development cycle: {cycle_id}"
    )
