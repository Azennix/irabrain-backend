from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import Lock
from types import SimpleNamespace


# =====================================================
# GUEST SESSION CONFIGURATION
# =====================================================

GUEST_MAX_TURNS = 5
GUEST_SESSION_TTL_MINUTES = 60


# =====================================================
# GUEST SESSION
# =====================================================

@dataclass
class GuestSession:
    session_id: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_activity: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    turn_count: int = 0
    messages: list[dict[str, str]] = field(default_factory=list)


# =====================================================
# GUEST SESSION SERVICE
# =====================================================

class GuestSessionService:

    def __init__(self):
        self._sessions: dict[str, GuestSession] = {}
        self._lock = Lock()

    # -------------------------------------------------
    # CREATE / GET SESSION
    # -------------------------------------------------

    def get_or_create(
        self,
        session_id: str,
    ) -> GuestSession:

        now = datetime.now(timezone.utc)

        with self._lock:

            session = self._sessions.get(session_id)

            if session is None:
                session = GuestSession(
                    session_id=session_id,
                )

                self._sessions[session_id] = session

            elif self._is_expired(session, now):
                session = GuestSession(
                    session_id=session_id,
                )

                self._sessions[session_id] = session

            session.last_activity = now

            return session

    # -------------------------------------------------
    # RESERVE TURN
    # -------------------------------------------------

    def reserve_turn(
        self,
        session_id: str,
    ) -> bool:

        now = datetime.now(timezone.utc)

        with self._lock:

            session = self._sessions.get(session_id)

            if session is None:
                session = GuestSession(
                    session_id=session_id,
                )

                self._sessions[session_id] = session

            elif self._is_expired(session, now):
                session = GuestSession(
                    session_id=session_id,
                )

                self._sessions[session_id] = session

            # -----------------------------------------
            # HARD 5-TURN LIMIT
            # -----------------------------------------

            if session.turn_count >= GUEST_MAX_TURNS:
                return False

            # Reserve the turn BEFORE the AI is called.
            session.turn_count += 1
            session.last_activity = now

            return True

    # -------------------------------------------------
    # ADD MESSAGE
    # -------------------------------------------------

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        with self._lock:

            session = self._sessions.get(session_id)

            if session is None:
                return

            session.messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

            session.last_activity = (
                datetime.now(timezone.utc)
            )

    # -------------------------------------------------
    # GET MESSAGES
    # -------------------------------------------------

    def get_messages(self,session_id):
        with self._lock:
            session=self._sessions.get(session_id)

            if session is None:
                return []

            return [
                SimpleNamespace(
                    role=message["role"],
                    content=message["content"]
            )
                for message in session.messages
        ]

    # -------------------------------------------------
    # TURN COUNT
    # -------------------------------------------------

    def get_turn_count(
        self,
        session_id: str,
    ) -> int:

        with self._lock:

            session = self._sessions.get(session_id)

            if session is None:
                return 0

            return session.turn_count

    # -------------------------------------------------
    # DELETE SESSION
    # -------------------------------------------------

    def delete(
        self,
        session_id: str,
    ) -> None:

        with self._lock:
            self._sessions.pop(
                session_id,
                None,
            )

    # -------------------------------------------------
    # CLEANUP EXPIRED SESSIONS
    # -------------------------------------------------

    def cleanup_expired(self) -> None:

        now = datetime.now(timezone.utc)

        with self._lock:

            expired_sessions = [
                session_id
                for session_id, session
                in self._sessions.items()
                if self._is_expired(
                    session,
                    now,
                )
            ]

            for session_id in expired_sessions:
                self._sessions.pop(
                    session_id,
                    None,
                )

    # -------------------------------------------------
    # INTERNAL EXPIRATION CHECK
    # -------------------------------------------------

    @staticmethod
    def _is_expired(
        session: GuestSession,
        now: datetime,
    ) -> bool:

        return (
            now - session.last_activity
            >= timedelta(
                minutes=GUEST_SESSION_TTL_MINUTES
            )
        )


# =====================================================
# SHARED SERVICE INSTANCE
# =====================================================

guest_session_service = GuestSessionService()