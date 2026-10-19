from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import subprocess


@dataclass(frozen=True)
class BuildResult:
    """
    Result of a build operation.
    """

    success: bool
    command: str
    return_code: int
    stdout: str
    stderr: str
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )


class BuildExecutor:
    """
    Executes an approved build command for a development candidate.

    Responsibilities:
    - run a supplied build command
    - capture stdout and stderr
    - capture the exit code
    - return structured build evidence

    It does NOT:
    - modify source code
    - deploy changes
    - release versions
    - decide production eligibility
    """

    def __init__(
        self,
        timeout_seconds: int = 600,
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
    ) -> BuildResult:

        if not command:
            raise ValueError(
                "Build command cannot be empty."
            )

        completed = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            shell=False,
        )

        return BuildResult(
            success=completed.returncode == 0,
            command=" ".join(command),
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )