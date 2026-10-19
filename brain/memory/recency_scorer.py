from datetime import datetime, timezone
from math import exp


class RecencyScorer:

    def score(
        self,
        last_accessed: datetime | None
    ) -> float:

        if last_accessed is None:
            return 0.0

        now = datetime.now(timezone.utc)

        if last_accessed.tzinfo is None:
            last_accessed = last_accessed.replace(
                tzinfo=timezone.utc
            )

        age_seconds = (
            now - last_accessed
        ).total_seconds()

        if age_seconds < 0:
            age_seconds = 0

        days = age_seconds / 86400

        return exp(-days / 30)