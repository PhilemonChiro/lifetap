"""
Conversation State Manager for WhatsApp Chatbot

Manages conversation state for each user session, storing partial data
as users progress through multi-step flows like emergency registration.
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class ConversationState(Enum):
    """Conversation flow states."""
    IDLE = "idle"

    # Emergency Flow States
    EMERGENCY_START = "emergency_start"
    EMERGENCY_TYPE = "emergency_type"
    EMERGENCY_CONSCIOUS = "emergency_conscious"
    EMERGENCY_BREATHING = "emergency_breathing"
    EMERGENCY_VICTIM_COUNT = "emergency_victim_count"
    EMERGENCY_SCENE = "emergency_scene"
    EMERGENCY_LOCATION = "emergency_location"
    EMERGENCY_CONFIRMED = "emergency_confirmed"

    # Registration Flow States
    REGISTER_START = "register_start"
    REGISTER_NAME = "register_name"
    REGISTER_DOB = "register_dob"
    REGISTER_GENDER = "register_gender"
    REGISTER_TIER = "register_tier"
    REGISTER_NOK = "register_nok"
    REGISTER_PAYMENT = "register_payment"

    # Profile Update States
    PROFILE_MENU = "profile_menu"
    PROFILE_EMR = "profile_emr"
    PROFILE_NOK = "profile_nok"


class ConversationSession:
    """Stores conversation state and collected data for a user session."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        self.state = ConversationState.IDLE
        self.data = {}
        self.member_id = None
        self.member_data = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=30)

    def set_state(self, state: ConversationState):
        """Update conversation state."""
        self.state = state
        self.updated_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(minutes=30)

    def set_data(self, key: str, value):
        """Store collected data."""
        self.data[key] = value
        self.updated_at = datetime.now()

    def get_data(self, key: str, default=None):
        """Retrieve collected data."""
        return self.data.get(key, default)

    def clear(self):
        """Reset session to idle state."""
        self.state = ConversationState.IDLE
        self.data = {}
        self.updated_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.now() > self.expires_at


class ConversationManager:
    """
    Manages conversation sessions for all users.

    In production, this should use Redis or database storage.
    For now, uses in-memory storage with expiration.
    """

    def __init__(self):
        self._sessions: dict[str, ConversationSession] = {}

    def get_session(self, phone_number: str) -> ConversationSession:
        """Get or create a session for a phone number."""
        # Clean expired sessions periodically
        self._cleanup_expired()

        if phone_number not in self._sessions:
            self._sessions[phone_number] = ConversationSession(phone_number)

        session = self._sessions[phone_number]

        # Reset if expired
        if session.is_expired():
            session.clear()

        return session

    def clear_session(self, phone_number: str):
        """Clear a user's session."""
        if phone_number in self._sessions:
            self._sessions[phone_number].clear()

    def _cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired = [
            phone for phone, session in self._sessions.items()
            if session.is_expired()
        ]
        for phone in expired:
            del self._sessions[phone]


# Global conversation manager instance
conversation_manager = ConversationManager()
