from dataclasses import dataclass, field
from threading import Lock
from types import SimpleNamespace


@dataclass
class PrivateSession:
    session_id: str
    messages: list[dict[str, str]] = field(
        default_factory=list
    )


class PrivateSessionService:

    def __init__(self):
        self._sessions: dict[str, PrivateSession] = {}
        self._lock = Lock()

    # =====================================================
    # GET OR CREATE SESSION
    # =====================================================

    def get_or_create(
        self,
        session_id: str
    ) -> PrivateSession:

        with self._lock:

            session = self._sessions.get(
                session_id
            )

            if session is None:

                session = PrivateSession(
                    session_id=session_id
                )

                self._sessions[
                    session_id
                ] = session

            return session

    # =====================================================
    # ADD MESSAGE
    # =====================================================

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> None:

        session = self.get_or_create(
            session_id
        )

        with self._lock:

            session.messages.append(
                {
                    "role": role,
                    "content": content
                }
            )

    # =====================================================
    # GET MESSAGES
    # =====================================================

    def get_messages(self, session_id: str):
            session = self.get_or_create(session_id)

            with self._lock:
                return [
                    SimpleNamespace(
                       role=message["role"],
                       content=message["content"]
            )
                    for message in session.messages
        ]

    # =====================================================
    # DELETE SESSION
    # =====================================================

    def delete(
        self,
        session_id: str
    ) -> None:

        with self._lock:

            self._sessions.pop(
                session_id,
                None
            )

private_session_service = PrivateSessionService()