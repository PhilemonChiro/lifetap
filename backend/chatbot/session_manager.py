"""
Session Manager for LifeTap WhatsApp Chatbot

Manages conversation state for each user session with in-memory caching.
Can be extended to Redis for multi-worker deployments.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation flow states for emergency activation."""

    # Initial/Idle
    START = "start"
    IDLE = "idle"

    # Emergency Flow States (triggered by NFC/QR scan)
    EMERGENCY_TRIGGERED = "emergency_triggered"      # NFC scanned, member found
    EMERGENCY_TYPE = "emergency_type"                # What happened?
    EMERGENCY_CONSCIOUS = "emergency_conscious"      # Is person conscious?
    EMERGENCY_BREATHING = "emergency_breathing"      # Is person breathing?
    EMERGENCY_VICTIM_COUNT = "emergency_victim_count"  # How many victims?
    EMERGENCY_SCENE = "emergency_scene"              # Scene description (optional)
    EMERGENCY_SCENE_INPUT = "emergency_scene_input"  # Waiting for text input
    EMERGENCY_LOCATION = "emergency_location"        # Requesting GPS location
    EMERGENCY_CONFIRMED = "emergency_confirmed"      # Incident created

    # Completed
    COMPLETED = "completed"


@dataclass
class Session:
    """
    Stores conversation state and collected data for a user session.

    Attributes:
        user_id: Phone number (unique identifier)
        state: Current conversation state
        data: Temporary data storage for flow
        created_at: Session creation timestamp
        last_activity: Last interaction timestamp
    """
    user_id: str
    state: ConversationState = ConversationState.START
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    # Member data (loaded when emergency triggered)
    member_id: Optional[str] = None
    member_uuid: Optional[str] = None
    member_name: Optional[str] = None
    member_data: Optional[Dict] = None

    def set_state(self, state: ConversationState) -> None:
        """Update conversation state and refresh activity timestamp."""
        logger.info(f"Session {self.user_id}: {self.state.value} -> {state.value}")
        self.state = state
        self.last_activity = datetime.now()

    def set_data(self, key: str, value: Any) -> None:
        """Store collected data."""
        self.data[key] = value
        self.last_activity = datetime.now()

    def get_data(self, key: str, default: Any = None) -> Any:
        """Retrieve collected data."""
        return self.data.get(key, default)

    def clear_data(self) -> None:
        """Clear all collected data but keep session."""
        self.data = {}
        self.member_id = None
        self.member_uuid = None
        self.member_name = None
        self.member_data = None

    def reset(self) -> None:
        """Reset session to initial state."""
        self.state = ConversationState.START
        self.clear_data()
        self.last_activity = datetime.now()

    def is_expired(self, ttl_minutes: int = 30) -> bool:
        """Check if session has expired."""
        expiry = self.last_activity + timedelta(minutes=ttl_minutes)
        return datetime.now() > expiry

    def is_in_flow(self) -> bool:
        """Check if user is in an active emergency flow."""
        active_states = [
            ConversationState.EMERGENCY_TRIGGERED,
            ConversationState.EMERGENCY_TYPE,
            ConversationState.EMERGENCY_CONSCIOUS,
            ConversationState.EMERGENCY_BREATHING,
            ConversationState.EMERGENCY_VICTIM_COUNT,
            ConversationState.EMERGENCY_SCENE,
            ConversationState.EMERGENCY_SCENE_INPUT,
            ConversationState.EMERGENCY_LOCATION,
        ]
        return self.state in active_states


class SessionManager:
    """
    Manages conversation sessions for all users.

    Uses in-memory storage with automatic expiration cleanup.
    For production multi-worker deployments, extend to use Redis.
    """

    def __init__(self, ttl_minutes: int = 30, max_sessions: int = 10000):
        """
        Initialize session manager.

        Args:
            ttl_minutes: Session time-to-live in minutes
            max_sessions: Maximum sessions to keep in memory
        """
        self._sessions: Dict[str, Session] = {}
        self._ttl_minutes = ttl_minutes
        self._max_sessions = max_sessions
        self._last_cleanup = datetime.now()
        logger.info(f"SessionManager initialized (TTL: {ttl_minutes}min, max: {max_sessions})")

    def get_session(self, user_id: str) -> Session:
        """
        Get or create a session for a user.

        Args:
            user_id: Phone number (unique identifier)

        Returns:
            Session object for the user
        """
        # Periodic cleanup
        self._cleanup_if_needed()

        # Get existing session
        if user_id in self._sessions:
            session = self._sessions[user_id]

            # Reset if expired
            if session.is_expired(self._ttl_minutes):
                logger.info(f"Session expired for {user_id}, resetting")
                session.reset()

            return session

        # Create new session
        session = Session(user_id=user_id)
        self._sessions[user_id] = session
        logger.info(f"New session created for {user_id}")

        return session

    def save_session(self, session: Session) -> None:
        """
        Save session (for Redis compatibility).

        In-memory implementation just updates the reference.
        """
        self._sessions[session.user_id] = session

    def delete_session(self, user_id: str) -> None:
        """Delete a user's session."""
        if user_id in self._sessions:
            del self._sessions[user_id]
            logger.info(f"Session deleted for {user_id}")

    def reset_session(self, user_id: str) -> Session:
        """Reset a user's session to initial state."""
        session = self.get_session(user_id)
        session.reset()
        return session

    def get_active_count(self) -> int:
        """Get count of active (non-expired) sessions."""
        self._cleanup_expired()
        return len(self._sessions)

    def _cleanup_if_needed(self) -> None:
        """Cleanup expired sessions if enough time has passed."""
        # Cleanup every 5 minutes
        if (datetime.now() - self._last_cleanup).seconds > 300:
            self._cleanup_expired()
            self._last_cleanup = datetime.now()

    def _cleanup_expired(self) -> None:
        """Remove expired sessions."""
        expired = [
            user_id for user_id, session in self._sessions.items()
            if session.is_expired(self._ttl_minutes)
        ]

        for user_id in expired:
            del self._sessions[user_id]

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        # Enforce max sessions limit (remove oldest)
        if len(self._sessions) > self._max_sessions:
            sorted_sessions = sorted(
                self._sessions.items(),
                key=lambda x: x[1].last_activity
            )
            remove_count = len(self._sessions) - self._max_sessions
            for user_id, _ in sorted_sessions[:remove_count]:
                del self._sessions[user_id]
            logger.info(f"Removed {remove_count} oldest sessions (max limit)")


# Global session manager instance
session_manager = SessionManager()
