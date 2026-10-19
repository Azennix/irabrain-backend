from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ReleaseDecision:
    """
    Result of release-policy evaluation.
    """

    eligible: bool
    reasons: List[str] = field(
        default_factory=list
    )


@dataclass
class ReleasePolicy:
    """
    Defines the minimum conditions required
    for a candidate to become release-eligible.

    This policy does NOT perform the release.
    """

    require_tests: bool = True
    require_build: bool = True
    require_lint: bool = True
    require_evaluation: bool = True
    require_no_regression: bool = True
    require_staging: bool = True
    require_canary: bool = True

    def evaluate(
        self,
        evidence: Dict,
    ) -> ReleaseDecision:

        if evidence is None:
            raise ValueError(
                "Release evidence cannot be None."
            )

        reasons = []

        requirements = {
            "tests": self.require_tests,
            "build": self.require_build,
            "lint": self.require_lint,
            "evaluation": self.require_evaluation,
            "no_regression": self.require_no_regression,
            "staging": self.require_staging,
            "canary": self.require_canary,
        }

        for requirement, required in requirements.items():

            if not required:
                continue

            if evidence.get(requirement) is not True:
                reasons.append(
                    f"Required condition not satisfied: "
                    f"{requirement}"
                )

        return ReleaseDecision(
            eligible=not reasons,
            reasons=reasons,
        )

    def snapshot(self) -> Dict[str, bool]:
        """
        Return the current release policy.
        """

        return {
            "require_tests": self.require_tests,
            "require_build": self.require_build,
            "require_lint": self.require_lint,
            "require_evaluation": self.require_evaluation,
            "require_no_regression": (
                self.require_no_regression
            ),
            "require_staging": self.require_staging,
            "require_canary": self.require_canary,
        }