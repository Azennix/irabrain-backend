from dataclasses import dataclass
from typing import Dict, Set

from brain.self_development.orchestrator.self_development_orchestrator import (
    SelfDevelopmentStage,
)


@dataclass(frozen=True)
class StageTransition:
    """
    Represents an allowed transition between
    self-development stages.
    """

    source: SelfDevelopmentStage
    target: SelfDevelopmentStage


class StageController:
    """
    Controls valid stage transitions for the
    self-development pipeline.

    Responsibilities:
    - define valid stage transitions
    - validate requested transitions
    - prevent invalid pipeline jumps

    It does NOT:
    - execute development
    - modify source code
    - run tests
    - deploy releases
    - make release decisions
    """

    def __init__(self):
        self._transitions: Dict[
            SelfDevelopmentStage,
            Set[SelfDevelopmentStage],
        ] = {
            SelfDevelopmentStage.CREATED: {
                SelfDevelopmentStage.OBSERVATION,
            },

            SelfDevelopmentStage.OBSERVATION: {
                SelfDevelopmentStage.INVESTIGATION,
                SelfDevelopmentStage.FAILED,
            },

            SelfDevelopmentStage.INVESTIGATION: {
                SelfDevelopmentStage.PLANNING,
                SelfDevelopmentStage.FAILED,
            },

            SelfDevelopmentStage.PLANNING: {
                SelfDevelopmentStage.DEVELOPMENT,
                SelfDevelopmentStage.FAILED,
            },

            SelfDevelopmentStage.DEVELOPMENT: {
                SelfDevelopmentStage.LINTING,
                SelfDevelopmentStage.FAILED,
},


            SelfDevelopmentStage.LINTING: {
                SelfDevelopmentStage.TESTING,
                SelfDevelopmentStage.FAILED,
},


            SelfDevelopmentStage.TESTING: {
                SelfDevelopmentStage.BUILD,
                SelfDevelopmentStage.FAILED,
            },
            SelfDevelopmentStage.BUILD: {
                SelfDevelopmentStage.EVALUATION,
                SelfDevelopmentStage.FAILED,
},

            SelfDevelopmentStage.EVALUATION: {
                SelfDevelopmentStage.STAGING,
                SelfDevelopmentStage.FAILED,
                SelfDevelopmentStage.ROLLED_BACK,
            },

            SelfDevelopmentStage.STAGING: {
                SelfDevelopmentStage.CANARY,
                SelfDevelopmentStage.FAILED,
                SelfDevelopmentStage.ROLLED_BACK,
            },

            SelfDevelopmentStage.CANARY: {
                SelfDevelopmentStage.RELEASE,
                SelfDevelopmentStage.FAILED,
                SelfDevelopmentStage.ROLLED_BACK,
            },

            SelfDevelopmentStage.RELEASE: {
                SelfDevelopmentStage.COMPLETED,
                SelfDevelopmentStage.FAILED,
                SelfDevelopmentStage.ROLLED_BACK,
            },

            SelfDevelopmentStage.COMPLETED: set(),

            SelfDevelopmentStage.FAILED: {
                SelfDevelopmentStage.ROLLED_BACK,
            },

            SelfDevelopmentStage.ROLLED_BACK: set(),
        }

    def can_transition(
        self,
        source: SelfDevelopmentStage,
        target: SelfDevelopmentStage,
    ) -> bool:

        if not isinstance(
            source,
            SelfDevelopmentStage,
        ):
            raise ValueError(
                "Invalid source stage."
            )

        if not isinstance(
            target,
            SelfDevelopmentStage,
        ):
            raise ValueError(
                "Invalid target stage."
            )

        return target in self._transitions.get(
            source,
            set(),
        )

    def validate_transition(
        self,
        source: SelfDevelopmentStage,
        target: SelfDevelopmentStage,
    ) -> None:

        if not self.can_transition(
            source,
            target,
        ):
            raise ValueError(
                f"Invalid self-development transition: "
                f"{source.value} -> {target.value}"
            )

    def allowed_next_stages(
        self,
        source: SelfDevelopmentStage,
    ) -> Set[SelfDevelopmentStage]:

        if not isinstance(
            source,
            SelfDevelopmentStage,
        ):
            raise ValueError(
                "Invalid source stage."
            )

        return set(
            self._transitions.get(
                source,
                set(),
            )
        )