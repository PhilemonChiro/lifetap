"""
Emergency Flow Handler for LifeTap WhatsApp Chatbot

Handles the emergency conversation flow when bystander scans NFC/QR card.
NFC card URL format: wa.me/{phone}?text=EMERGENCY:LT-2025-A7X9K3

Flow:
1. EMERGENCY_TRIGGERED - Member found, show medical info
2. EMERGENCY_TYPE - What happened? (list selection)
3. EMERGENCY_CONSCIOUS - Is person conscious? (buttons)
4. EMERGENCY_BREATHING - Is person breathing? (buttons)
5. EMERGENCY_VICTIM_COUNT - How many victims? (list)
6. EMERGENCY_SCENE - Optional scene description
7. EMERGENCY_LOCATION - GPS location request
8. EMERGENCY_CONFIRMED - Incident created, dispatch started
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from .session_manager import Session, ConversationState, session_manager
from . import messages

logger = logging.getLogger(__name__)


class MessageHandler:
    """
    Main message handler for emergency chatbot.

    Routes incoming messages based on session state and handles
    the multi-step emergency data collection flow.
    """

    def __init__(self, supabase_client):
        """
        Initialize handler with Supabase client.

        Args:
            supabase_client: Initialized Supabase client
        """
        self.supabase = supabase_client
        self._processed_messages: Dict[str, datetime] = {}
        self._max_cache_size = 1000
        logger.info("MessageHandler initialized")

    # =========================================================================
    # MESSAGE ROUTING
    # =========================================================================

    async def process_message(
        self,
        user_id: str,
        message_type: str,
        message_data: Dict[str, Any],
        message_id: Optional[str] = None
    ) -> Dict:
        """
        Process an incoming WhatsApp message.

        Args:
            user_id: Phone number of sender
            message_type: Type of message (text, interactive, location)
            message_data: Message content
            message_id: WhatsApp message ID for deduplication

        Returns:
            Response dict with status
        """
        # Deduplication check
        if message_id and self._is_duplicate(message_id):
            logger.info(f"Duplicate message ignored: {message_id}")
            return {"status": "duplicate"}

        # Get or create session
        session = session_manager.get_session(user_id)
        logger.info(f"Processing {message_type} for {user_id} in state {session.state.value}")

        try:
            # Route based on message type
            if message_type == "text":
                return await self._handle_text(session, message_data)

            elif message_type == "interactive":
                return await self._handle_interactive(session, message_data)

            elif message_type == "location":
                return await self._handle_location(session, message_data)

            else:
                logger.info(f"Unsupported message type: {message_type}")
                return await self._send_help_message(session)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            messages.send_text(
                user_id,
                "Sorry, something went wrong. Please try again or call emergency services directly."
            )
            return {"status": "error", "error": str(e)}

    def _is_duplicate(self, message_id: str) -> bool:
        """Check if message was already processed."""
        now = datetime.now()

        # Cleanup old entries
        cutoff = datetime.now()
        self._processed_messages = {
            mid: ts for mid, ts in self._processed_messages.items()
            if (cutoff - ts).seconds < 300  # 5 minute window
        }

        # Enforce max cache size
        if len(self._processed_messages) > self._max_cache_size:
            oldest = sorted(self._processed_messages.items(), key=lambda x: x[1])
            for mid, _ in oldest[:self._max_cache_size // 5]:
                del self._processed_messages[mid]

        # Check and add
        if message_id in self._processed_messages:
            return True

        self._processed_messages[message_id] = now
        return False

    # =========================================================================
    # TEXT MESSAGE HANDLING
    # =========================================================================

    async def _handle_text(self, session: Session, data: Dict) -> Dict:
        """Handle text message based on current state."""
        text = data.get("body", "").strip()
        user_id = session.user_id

        logger.info(f"Text from {user_id}: {text[:50]}...")

        # Check for emergency trigger (NFC/QR scan)
        if text.upper().startswith("EMERGENCY:"):
            member_id = text.split(":", 1)[1].strip().upper()
            return await self._start_emergency(session, member_id)

        # Direct member ID (backup trigger)
        if text.upper().startswith("LT-"):
            return await self._start_emergency(session, text.upper())

        # Handle based on current state
        state = session.state

        if state == ConversationState.EMERGENCY_SCENE_INPUT:
            # Collecting scene description text
            return await self._handle_scene_input(session, text)

        elif session.is_in_flow():
            # In active flow but got unexpected text
            return await self._handle_unexpected_input(session, "text")

        else:
            # Not in flow - send help message
            return await self._send_help_message(session)

    # =========================================================================
    # INTERACTIVE MESSAGE HANDLING (Buttons & Lists)
    # =========================================================================

    async def _handle_interactive(self, session: Session, data: Dict) -> Dict:
        """Handle interactive message (button or list selection)."""
        user_id = session.user_id

        # Debug log the raw data
        logger.info(f"Interactive data received: {data}")

        interactive_type = data.get("type")

        # Extract selection ID based on interactive type
        selection_id = ""
        if interactive_type == "button_reply":
            button_reply = data.get("button_reply", {})
            selection_id = button_reply.get("id", "") if isinstance(button_reply, dict) else ""
            logger.info(f"Button reply parsed: {button_reply} -> id={selection_id}")
        elif interactive_type == "list_reply":
            list_reply = data.get("list_reply", {})
            selection_id = list_reply.get("id", "") if isinstance(list_reply, dict) else ""
            logger.info(f"List reply parsed: {list_reply} -> id={selection_id}")
        else:
            logger.warning(f"Unknown interactive type: {interactive_type}, data: {data}")
            return {"status": "ignored"}

        if not selection_id:
            logger.warning(f"No selection_id extracted from interactive message")
            return {"status": "no_selection"}

        logger.info(f"Interactive from {user_id}: type={interactive_type}, selection={selection_id}, state={session.state.value}")

        # Route based on state
        state = session.state

        if state == ConversationState.EMERGENCY_TYPE:
            return await self._handle_emergency_type(session, selection_id)

        elif state == ConversationState.EMERGENCY_CONSCIOUS:
            return await self._handle_conscious(session, selection_id)

        elif state == ConversationState.EMERGENCY_BREATHING:
            return await self._handle_breathing(session, selection_id)

        elif state == ConversationState.EMERGENCY_VICTIM_COUNT:
            return await self._handle_victim_count(session, selection_id)

        elif state == ConversationState.EMERGENCY_SCENE:
            return await self._handle_scene_option(session, selection_id)

        elif not session.is_in_flow():
            # Not in flow - ignore stale button clicks
            logger.info(f"Ignoring interactive - no active flow")
            return {"status": "ignored"}

        else:
            return await self._handle_unexpected_input(session, "interactive")

    # =========================================================================
    # LOCATION HANDLING
    # =========================================================================

    async def _handle_location(self, session: Session, data: Dict) -> Dict:
        """Handle location message."""
        user_id = session.user_id
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        address = data.get("address") or data.get("name")

        logger.info(f"Location from {user_id}: {latitude}, {longitude}")

        if session.state == ConversationState.EMERGENCY_LOCATION:
            return await self._handle_location_received(session, latitude, longitude, address)

        elif session.is_in_flow():
            # Got location at wrong step - save it anyway and continue
            session.set_data("latitude", latitude)
            session.set_data("longitude", longitude)
            session.set_data("address", address)
            messages.send_text(user_id, "Location saved. Please continue with the current question.")
            return {"status": "saved"}

        else:
            # Not in flow
            return await self._send_help_message(session)

    # =========================================================================
    # EMERGENCY FLOW: START
    # =========================================================================

    async def _start_emergency(self, session: Session, member_id: str) -> Dict:
        """
        Start emergency flow when NFC/QR is scanned.

        Args:
            session: User session
            member_id: Member ID from scanned card (LT-2025-XXXXX)
        """
        user_id = session.user_id
        logger.info(f"Emergency triggered for {member_id} by {user_id}")

        # Reset any existing flow
        session.reset()

        # Look up member
        member = await self._get_member(member_id)

        if not member:
            logger.warning(f"Member not found: {member_id}")
            messages.send_text(
                user_id,
                f"*MEMBER NOT FOUND*\n\n"
                f"ID: {member_id}\n\n"
                f"Please verify the card and try again, or call emergency services directly:\n\n"
                f"*MARS:* 0242 700991\n"
                f"*Netstar:* 0772 390 303"
            )
            return {"status": "member_not_found"}

        # Store member info in session
        session.member_id = member_id
        session.member_uuid = member.get("id")
        session.member_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
        session.member_data = member

        # Get EMR data
        emr = member.get("emr_records") or {}
        if isinstance(emr, list) and emr:
            emr = emr[0]

        session.set_data("blood_type", emr.get("blood_type", "Unknown"))
        session.set_data("allergies", self._format_list(emr.get("allergies", [])) or "None known")
        session.set_data("conditions", self._format_list(emr.get("chronic_conditions", [])) or "None known")

        # Check subscription and get tier
        subscriptions = member.get("subscriptions", [])
        active_sub = next((s for s in subscriptions if s.get("status") == "active"), None)

        if active_sub:
            # Get tier info from subscription
            tier_info = active_sub.get("tiers", {})
            tier_name = tier_info.get("name", "lifeline") if tier_info else "lifeline"
            session.set_data("member_tier", tier_name)
            logger.info(f"Member {member_id} has active {tier_name} subscription")
        else:
            logger.warning(f"Subscription expired for {member_id}")
            session.set_data("member_tier", None)
            messages.send_text(
                user_id,
                f"*SUBSCRIPTION EXPIRED*\n\n"
                f"*Member:* {session.member_name}\n\n"
                f"Emergency services will still be dispatched, but coverage may not apply."
            )

        # Set state and send first message
        session.set_state(ConversationState.EMERGENCY_TRIGGERED)

        # Send header with medical info
        messages.send_emergency_header(
            to=user_id,
            member_name=session.member_name,
            member_id=member_id,
            blood_type=session.get_data("blood_type"),
            allergies=session.get_data("allergies"),
            conditions=session.get_data("conditions")
        )

        # Move to emergency type selection
        session.set_state(ConversationState.EMERGENCY_TYPE)
        messages.send_emergency_type_list(user_id)

        session_manager.save_session(session)
        return {"status": "started", "member_id": member_id}

    # =========================================================================
    # EMERGENCY FLOW: STEP HANDLERS
    # =========================================================================

    async def _handle_emergency_type(self, session: Session, selection: str) -> Dict:
        """Handle emergency type selection."""
        user_id = session.user_id

        # Map selection to emergency type
        emergency_types = {
            "road_accident": "Road Accident",
            "collapse": "Person Collapsed",
            "heart_attack": "Chest Pain / Heart Attack",
            "breathing": "Breathing Difficulty",
            "injury": "Serious Injury / Bleeding",
            "seizure": "Seizure / Convulsion",
            "burn": "Burn",
            "other": "Other Medical Emergency"
        }

        emergency_type = emergency_types.get(selection, selection)
        session.set_data("emergency_type", emergency_type)
        session.set_data("emergency_type_id", selection)

        logger.info(f"Emergency type: {emergency_type}")

        # Move to consciousness check
        session.set_state(ConversationState.EMERGENCY_CONSCIOUS)
        messages.send_conscious_buttons(user_id)

        session_manager.save_session(session)
        return {"status": "ok", "step": "emergency_type"}

    async def _handle_conscious(self, session: Session, selection: str) -> Dict:
        """Handle consciousness status."""
        user_id = session.user_id

        # Map button ID to value
        conscious_map = {
            "conscious_yes": "yes",
            "conscious_no": "no",
            "conscious_unsure": "unsure"
        }
        conscious = conscious_map.get(selection, selection)
        session.set_data("conscious", conscious)

        logger.info(f"Conscious: {conscious}")

        # Move to breathing check
        session.set_state(ConversationState.EMERGENCY_BREATHING)
        messages.send_breathing_buttons(user_id)

        session_manager.save_session(session)
        return {"status": "ok", "step": "conscious"}

    async def _handle_breathing(self, session: Session, selection: str) -> Dict:
        """Handle breathing status."""
        user_id = session.user_id

        # Map button ID to value
        breathing_map = {
            "breathing_yes": "yes",
            "breathing_struggling": "struggling",
            "breathing_no": "no"
        }
        breathing = breathing_map.get(selection, selection)
        session.set_data("breathing", breathing)

        logger.info(f"Breathing: {breathing}")

        # Move to victim count
        session.set_state(ConversationState.EMERGENCY_VICTIM_COUNT)
        messages.send_victim_count_list(user_id)

        session_manager.save_session(session)
        return {"status": "ok", "step": "breathing"}

    async def _handle_victim_count(self, session: Session, selection: str) -> Dict:
        """Handle victim count selection."""
        user_id = session.user_id

        # Map list ID to value
        count_map = {
            "victims_1": "1",
            "victims_2": "2",
            "victims_3": "3",
            "victims_4plus": "4+"
        }
        victim_count = count_map.get(selection, selection)
        session.set_data("victim_count", victim_count)

        logger.info(f"Victim count: {victim_count}")

        # Move to scene description (optional)
        session.set_state(ConversationState.EMERGENCY_SCENE)
        messages.send_scene_description_request(user_id)

        session_manager.save_session(session)
        return {"status": "ok", "step": "victim_count"}

    async def _handle_scene_option(self, session: Session, selection: str) -> Dict:
        """Handle scene description option (skip or add)."""
        user_id = session.user_id

        if selection == "scene_skip":
            # Skip scene description, go to location
            session.set_data("scene_description", None)
            session.set_state(ConversationState.EMERGENCY_LOCATION)
            messages.send_location_request_emergency(user_id)

        elif selection == "scene_describe":
            # Wait for text input
            session.set_state(ConversationState.EMERGENCY_SCENE_INPUT)
            messages.send_text(user_id, "Please describe the scene briefly:")

        session_manager.save_session(session)
        return {"status": "ok", "step": "scene_option"}

    async def _handle_scene_input(self, session: Session, text: str) -> Dict:
        """Handle scene description text input."""
        user_id = session.user_id

        session.set_data("scene_description", text)
        logger.info(f"Scene description: {text[:50]}...")

        # Move to location request
        session.set_state(ConversationState.EMERGENCY_LOCATION)
        messages.send_location_request_emergency(user_id)

        session_manager.save_session(session)
        return {"status": "ok", "step": "scene_input"}

    async def _handle_location_received(
        self, session: Session, latitude: float, longitude: float, address: Optional[str]
    ) -> Dict:
        """Handle location received - create incident and send first aid guidance."""
        user_id = session.user_id

        session.set_data("latitude", latitude)
        session.set_data("longitude", longitude)
        session.set_data("address", address)

        logger.info(f"Location received: {latitude}, {longitude}")

        # Create incident in database
        incident = await self._create_incident(session, user_id)

        if incident:
            session.set_data("incident_id", incident.get("id"))
            session.set_data("incident_number", incident.get("incident_number"))
            incident_number = incident.get("incident_number")

            # Send confirmation
            session.set_state(ConversationState.EMERGENCY_CONFIRMED)
            messages.send_emergency_confirmed(
                to=user_id,
                incident_number=incident_number,
                member_name=session.member_name
            )

            # Send first aid guidance based on emergency type
            emergency_type_id = session.get_data("emergency_type_id", "other")
            messages.send_first_aid_guidance(
                to=user_id,
                emergency_type=emergency_type_id
            )

            # Send "help on way" message with tracking
            messages.send_help_on_way(
                to=user_id,
                incident_number=incident_number,
                member_name=session.member_name
            )

            # Notify next of kin
            await self._notify_next_of_kin(session)

            # Reset session
            session.set_state(ConversationState.COMPLETED)
            session_manager.save_session(session)

            return {"status": "completed", "incident": incident}

        else:
            messages.send_text(
                user_id,
                "*ERROR*\n\n"
                "Failed to register emergency. Please call emergency services directly:\n\n"
                "*MARS:* 0242 700991\n"
                "*Netstar:* 0772 390 303"
            )
            return {"status": "error", "error": "Failed to create incident"}

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _send_help_message(self, session: Session) -> Dict:
        """Send help message for non-emergency queries."""
        messages.send_text(
            session.user_id,
            "*LifeTap Emergency Response*\n\n"
            "To activate emergency services, tap the NFC card or scan QR code on a member's LifeTap card.\n\n"
            "For support: support@lifetap.co.zw"
        )
        return {"status": "help_sent"}

    async def _handle_unexpected_input(self, session: Session, input_type: str) -> Dict:
        """Handle unexpected input during flow."""
        user_id = session.user_id
        state = session.state

        logger.info(f"Unexpected {input_type} in state {state.value}")

        # Re-send the current step's prompt
        if state == ConversationState.EMERGENCY_TYPE:
            messages.send_emergency_type_list(user_id)
        elif state == ConversationState.EMERGENCY_CONSCIOUS:
            messages.send_conscious_buttons(user_id)
        elif state == ConversationState.EMERGENCY_BREATHING:
            messages.send_breathing_buttons(user_id)
        elif state == ConversationState.EMERGENCY_VICTIM_COUNT:
            messages.send_victim_count_list(user_id)
        elif state == ConversationState.EMERGENCY_SCENE:
            messages.send_scene_description_request(user_id)
        elif state == ConversationState.EMERGENCY_LOCATION:
            messages.send_location_request_emergency(user_id)
        else:
            messages.send_text(user_id, "Please respond to the current question.")

        return {"status": "reprompted"}

    async def _get_member(self, member_id: str) -> Optional[Dict]:
        """Look up member by member_id."""
        try:
            result = self.supabase.table("members").select(
                "*, emr_records(*), subscriptions(*, tiers(*))"
            ).eq("member_id", member_id).execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error fetching member {member_id}: {e}")
            return None

    async def _create_incident(self, session: Session, bystander_phone: str) -> Optional[Dict]:
        """Create incident record in database."""
        try:
            # Generate incident number
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            incident_number = f"INC-{timestamp}"

            # Map breathing value
            breathing_val = session.get_data("breathing")
            patient_breathing = None
            if breathing_val == "yes":
                patient_breathing = True
            elif breathing_val == "no":
                patient_breathing = False

            # Map consciousness
            conscious_val = session.get_data("conscious")
            patient_conscious = None
            if conscious_val == "yes":
                patient_conscious = True
            elif conscious_val == "no":
                patient_conscious = False

            # Parse victim count
            victim_count_str = session.get_data("victim_count", "1")
            victim_count = 1
            if victim_count_str.startswith("4"):
                victim_count = 4
            elif victim_count_str.isdigit():
                victim_count = int(victim_count_str)

            incident_data = {
                "incident_number": incident_number,
                "member_id": session.member_uuid,
                "member_tier": session.get_data("member_tier"),
                "emergency_type": session.get_data("emergency_type_id"),
                "patient_conscious": patient_conscious,
                "patient_breathing": patient_breathing,
                "victim_count": victim_count,
                "scene_description": session.get_data("scene_description"),
                "gps_latitude": session.get_data("latitude"),
                "gps_longitude": session.get_data("longitude"),
                "address_description": session.get_data("address"),
                "activated_by_phone": bystander_phone,
                "activation_method": "whatsapp_chatbot",
                "status": "activated",
                "activated_at": datetime.now().isoformat()
            }

            result = self.supabase.table("incidents").insert(incident_data).execute()

            if result.data:
                logger.info(f"Incident created: {incident_number}")
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Error creating incident: {e}", exc_info=True)
            return None

    async def _notify_next_of_kin(self, session: Session) -> None:
        """Notify next of kin about the emergency."""
        try:
            member_uuid = session.member_uuid
            if not member_uuid:
                return

            # Get next of kin
            result = self.supabase.table("next_of_kin").select("*").eq(
                "member_id", member_uuid
            ).eq("is_primary", True).execute()

            if result.data:
                nok = result.data[0]
                nok_phone = nok.get("phone_number")

                if nok_phone:
                    messages.send_nok_alert(
                        to=nok_phone,
                        member_name=session.member_name,
                        incident_number=session.get_data("incident_number"),
                        location_description=session.get_data("address")
                    )
                    logger.info(f"NOK notified: {nok_phone}")

        except Exception as e:
            logger.error(f"Error notifying NOK: {e}")

    def _format_list(self, items) -> str:
        """Format list items as comma-separated string."""
        if isinstance(items, list):
            return ", ".join(str(item) for item in items if item)
        return str(items) if items else ""


# Alias for backwards compatibility
MainMenuHandler = MessageHandler
EmergencyHandler = MessageHandler
