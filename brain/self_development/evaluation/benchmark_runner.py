from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List


@dataclass(frozen=True)
class BenchmarkResult:
    benchmark_id: str
    success: bool
    score: float
    details: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class BenchmarkRun:
    results: List[BenchmarkResult]
    completed_at: datetime = field(
        default_factory=datetime.utcnow
    )

    @property
    def overall_score(self) -> float:
        if not self.results:
            return 0.0

        return sum(
            result.score
            for result in self.results
        ) / len(self.results)


class BenchmarkRunner:
    """
    Runs registered benchmarks against a candidate.

    Responsibilities:
    - register benchmark functions
    - execute benchmarks
    - collect benchmark results
    - calculate an overall score

    It does NOT:
    - modify source code
    - change baselines
    - release candidates
    - deploy anything
    """

    def __init__(self):
        self._benchmarks: Dict[
            str, Callable[[Any], BenchmarkResult]
        ] = {}

    def register(
        self,
        benchmark_id: str,
        benchmark: Callable[[Any], BenchmarkResult],
    ) -> None:

        if not benchmark_id.strip():
            raise ValueError(
                "Benchmark ID cannot be empty."
            )

        if not callable(benchmark):
            raise ValueError(
                "Benchmark must be callable."
            )

        self._benchmarks[benchmark_id] = benchmark

    def run(
        self,
        candidate: Any,
    ) -> BenchmarkRun:

        results: List[BenchmarkResult] = []

        for benchmark_id, benchmark in (
            self._benchmarks.items()
        ):
            result = benchmark(candidate)

            if not isinstance(
                result,
                BenchmarkResult,
            ):
                raise ValueError(
                    f"Benchmark '{benchmark_id}' "
                    "returned an invalid result."
                )

            results.append(result)

        return BenchmarkRun(
            results=results
        )

    def list_benchmarks(self) -> List[str]:
        return list(self._benchmarks.keys())