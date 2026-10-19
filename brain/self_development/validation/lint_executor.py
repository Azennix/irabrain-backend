from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import subprocess


@dataclass(frozen=True)
class LintResult:
    """
    Result of a lint operation.
    """

    success: bool
    command: str
    return_code: int
    stdout: str
    stderr: str
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class LintExecutor:
    """
    Executes an approved lint command against a development candidate.

    Responsibilities:
    - run a supplied lint command
    - capture stdout and stderr
    - capture the exit code
    - return structured lint evidence

    It does NOT:
    - modify source code
    - deploy changes
    - release versions
    - decide production eligibility
    """

    def __init__(
        self,
        timeout_seconds: int = 300,
    ):
        if timeout_seconds <= 0:
            raise ValueError(
                "Timeout must be greater than zero."
            )

        self.timeout_seconds = timeout_seconds

    def run(
        self,
        command: List[str],
        working_directory: Optional[str] = None,
    ) -> LintResult:

        if not command:
            raise ValueError(
                "Lint command cannot be empty."
            )

        completed = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            shell=False,
        )

        return LintResult(
            success=completed.returncode == 0,
            command=" ".join(command),
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )