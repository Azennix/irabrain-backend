from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import subprocess


@dataclass(frozen=True)
class TestResult:
    """
    Result of a test execution.
    """

    success: bool
    command: str
    return_code: int
    stdout: str
    stderr: str
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class TestExecutor:
    """
    Executes approved test commands for a development candidate.

    Responsibilities:
    - run a supplied test command
    - capture stdout and stderr
    - capture the exit code
    - return structured test evidence

    It does NOT:
    - modify source code
    - deploy changes
    - release versions
    - decide whether a change is safe for production
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
    ) -> TestResult:

        if not command:
            raise ValueError(
                "Test command cannot be empty."
            )

        completed = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            shell=False,
        )

        return TestResult(
            success=completed.returncode == 0,
            command=" ".join(command),
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )