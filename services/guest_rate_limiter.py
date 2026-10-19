from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import Lock


# =====================================================
# RATE LIMIT CONFIGURATION
# =====================================================

GUEST_RATE_LIMIT_REQUESTS = 10
GUEST_RATE_LIMIT_WINDOW_MINUTES = 10

GUEST_DEVICE_LIMIT_REQUESTS = 20
GUEST_DEVICE_LIMIT_WINDOW_MINUTES = 30


# =====================================================
# RATE LIMIT RECORD
# =====================================================

@dataclass
class RateLimitRecord:
    timestamps: list[datetime] = field(
        default_factory=list
    )


# =====================================================
# GUEST RATE LIMITER
# =====================================================

class GuestRateLimiter:

    def __init__(self):
        self._ip_records: dict[str, RateLimitRecord] = {}
        self._device_records: dict[str, RateLimitRecord] = {}
        self._lock = Lock()

    # -------------------------------------------------
    # CHECK REQUEST
    # -------------------------------------------------

    def allow_request(
        self,
        ip_key: str,
        device_key: str,
    ) -> bool:

        now = datetime.now(timezone.utc)

        with self._lock:

            ip_allowed = self._check_and_record(
                records=self._ip_records,
                key=ip_key,
                now=now,
                limit=GUEST_RATE_LIMIT_REQUESTS,
                window=timedelta(
                    minutes=GUEST_RATE_LIMIT_WINDOW_MINUTES
                ),
            )

            if not ip_allowed:
                return False

            device_allowed = self._check_and_record(
                records=self._device_records,
                key=device_key,
                now=now,
                limit=GUEST_DEVICE_LIMIT_REQUESTS,
                window=timedelta(
                    minutes=GUEST_DEVICE_LIMIT_WINDOW_MINUTES
                ),
            )

            return device_allowed

    # -------------------------------------------------
    # INTERNAL CHECK
    # -------------------------------------------------

    @staticmethod
    def _check_and_record(
        records: dict[str, RateLimitRecord],
        key: str,
        now: datetime,
        limit: int,
        window: timedelta,
    ) -> bool:

        record = records.get(key)

        if record is None:
            record = RateLimitRecord()
            records[key] = record

        cutoff = now - window

        record.timestamps = [
            timestamp
            for timestamp in record.timestamps
            if timestamp > cutoff
        ]

        if len(record.timestamps) >= limit:
            return False

        record.timestamps.append(now)

        return True

    # -------------------------------------------------
    # CLEANUP
    # -------------------------------------------------

    def cleanup(self) -> None:

        now = datetime.now(timezone.utc)

        with self._lock:

            self._cleanup_records(
                self._ip_records,
                now,
                timedelta(
                    minutes=GUEST_RATE_LIMIT_WINDOW_MINUTES
                ),
            )

            self._cleanup_records(
                self._device_records,
                now,
                timedelta(
                    minutes=GUEST_DEVICE_LIMIT_WINDOW_MINUTES
                ),
            )

    # -------------------------------------------------
    # INTERNAL CLEANUP
    # -------------------------------------------------

    @staticmethod
    def _cleanup_records(
        records: dict[str, RateLimitRecord],
        now: datetime,
        window: timedelta,
    ) -> None:

        cutoff = now - window

        expired_keys = []

        for key, record in records.items():

            record.timestamps = [
                timestamp
                for timestamp in record.timestamps
                if timestamp > cutoff
            ]

            if not record.timestamps:
                expired_keys.append(key)

        for key in expired_keys:
            records.pop(key, None)


# =====================================================
# SHARED INSTANCE
# =====================================================

guest_rate_limiter = GuestRateLimiter()