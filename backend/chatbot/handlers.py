"""
Emergency Flow Handler

Handles the emergency conversation flow when bystander scans NFC/QR card.
NFC card opens: wa.me/15550870762?text=EMERGENCY:LT-2025-A7X9K3
"""

import logging
from datetime import datetime
from typing import Optional

from .state import ConversationState, ConversationSession, conversation_manager
from . import messages

logger = logging.getLogger(__name__)


class EmergencyFlowHandler:
    """
    Handles the emergency registration conversation flow.

    Flow:
    1. Start emergency (from NFC/QR scan or menu)
    2. Select emergency type (list)
    3. Consciousness check (buttons)
    4. Breathing check (buttons)
    5. Victim count (list)
    6. Scene description (optional)
    7. Location request
    8. Confirmation & dispatch
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def start_emergency(self, session: ConversationSession, member_data: dict) -> None:
        """Start emergency flow with member data."""
        session.member_data = member_data
        session.member_id = member_data.get('member_id')

        # Store member info in session
        session.set_data('member_uuid', member_data.get('id'))
        session.set_data('member_name', f"{member_data.get('first_name', '')} {member_data.get('last_name', '')}".strip())

        # Get EMR data
        emr = member_data.get('emr_records') or {}
        if isinstance(emr, list) and emr:
            emr = emr[0]

        session.set_data('blood_type', emr.get('blood_type', 'Unknown'))
        session.set_data('allergies', self._format_list(emr.get('allergies', [])) or 'None known')
        session.set_data('conditions', self._format_list(emr.get('chronic_conditions', [])) or 'None known')

        # Set state to start collecting emergency info
        session.set_state(ConversationState.EMERGENCY_TYPE)

    def _format_list(self, items) -> str:
        """Format list items as comma-separated string."""
        if isinstance(items, list):
            return ', '.join(str(item) for item in items if item)
        return str(items) if items else ''

    def send_initial_message(self, to: str, session: ConversationSession) -> dict:
        """Send initial emergency header and first question."""
        # Send header with member info
        messages.send_emergency_header(
            to=to,
            member_name=session.get_data('member_name'),
            member_id=session.member_id,
            blood_type=session.get_data('blood_type'),
            allergies=session.get_data('allergies'),
            conditions=session.get_data('conditions')
        )

        # Send emergency type list
        return messages.send_emergency_type_list(to)

    def handle_input(self, session: ConversationSession, to: str, input_type: str, input_value: str) -> dict:
        """
        Process user input based on current state.

        Args:
            session: User's conversation session
            to: User's phone number
            input_type: Type of input ('text', 'button', 'list', 'location')
            input_value: The input value (button_id, list_row_id, text, or location dict)

        Returns:
            API response from sent message
        """
        state = session.state

        if state == ConversationState.EMERGENCY_TYPE:
            return self._handle_emergency_type(session, to, input_value)

        elif state == ConversationState.EMERGENCY_CONSCIOUS:
            return self._handle_conscious(session, to, input_value)

        elif state == ConversationState.EMERGENCY_BREATHING:
            return self._handle_breathing(session, to, input_value)

        elif state == ConversationState.EMERGENCY_VICTIM_COUNT:
            return self._handle_victim_count(session, to, input_value)

        elif state == ConversationState.EMERGENCY_SCENE:
            return self._handle_scene(session, to, input_type, input_value)

        elif state == ConversationState.EMERGENCY_LOCATION:
            return self._handle_location(session, to, input_type, input_value)

        else:
            # Unknown state, reset
            session.clear()
            return messages.send_text(to, "Sorry, something went wrong. Please try again.")

    def _handle_emergency_type(self, session: ConversationSession, to: str, emergency_type: str) -> dict:
        """Handle emergency type selection."""
        session.set_data('emergency_type', emergency_type)
        session.set_state(ConversationState.EMERGENCY_CONSCIOUS)
        return messages.send_conscious_buttons(to)

    def _handle_conscious(self, session: ConversationSession, to: str, conscious: str) -> dict:
        """Handle consciousness status."""
        # Map button IDs to values
        conscious_map = {
            'conscious_yes': 'yes',
            'conscious_no': 'no',
            'conscious_unsure': 'unsure'
        }
        session.set_data('conscious', conscious_map.get(conscious, conscious))
        session.set_state(ConversationState.EMERGENCY_BREATHING)
        return messages.send_breathing_buttons(to)

    def _handle_breathing(self, session: ConversationSession, to: str, breathing: str) -> dict:
        """Handle breathing status."""
        # Map button IDs to values
        breathing_map = {
            'breathing_yes': 'yes',
            'breathing_struggling': 'struggling',
            'breathing_no': 'no'
        }
        session.set_data('breathing', breathing_map.get(breathing, breathing))
        session.set_state(ConversationState.EMERGENCY_VICTIM_COUNT)
        return messages.send_victim_count_list(to)

    def _handle_victim_count(self, session: ConversationSession, to: str, victim_count: str) -> dict:
        """Handle victim count selection."""
        # Map list IDs to values
        count_map = {
            'victims_1': '1',
            'victims_2': '2',
            'victims_3': '3',
            'victims_4plus': '4+'
        }
        session.set_data('victim_count', count_map.get(victim_count, victim_count))
        session.set_state(ConversationState.EMERGENCY_SCENE)
        return messages.send_scene_description_request(to)

    def _handle_scene(self, session: ConversationSession, to: str, input_type: str, input_value: str) -> dict:
        """Handle scene description (optional)."""
        if input_type == 'button':
            if input_value == 'scene_skip':
                session.set_data('scene_description', None)
            elif input_value == 'scene_describe':
                # Wait for text input
                return messages.send_text(to, "Please describe the scene in a few words:")
        elif input_type == 'text':
            session.set_data('scene_description', input_value)

        # Move to location request
        session.set_state(ConversationState.EMERGENCY_LOCATION)
        return messages.send_location_request_emergency(to)

    def _handle_location(self, session: ConversationSession, to: str, input_type: str, input_value) -> dict:
        """Handle location input and create incident."""
        if input_type != 'location':
            # Remind them to share location
            return messages.send_location_request_emergency(to)

        # Extract location data
        latitude = input_value.get('latitude')
        longitude = input_value.get('longitude')
        address = input_value.get('address') or input_value.get('name')

        session.set_data('latitude', latitude)
        session.set_data('longitude', longitude)
        session.set_data('address', address)

        # Create incident in database
        incident = self._create_incident(session, to)

        if incident:
            session.set_data('incident_id', incident.get('id'))
            session.set_data('incident_number', incident.get('incident_number'))
            session.set_state(ConversationState.EMERGENCY_CONFIRMED)

            # Send confirmation
            messages.send_emergency_confirmed(
                to=to,
                incident_number=incident.get('incident_number'),
                member_name=session.get_data('member_name')
            )

            # Notify next of kin
            self._notify_next_of_kin(session)

            # Clear session after successful completion
            session.clear()

            return {'success': True, 'incident': incident}
        else:
            return messages.send_text(to, "Failed to register emergency. Please call emergency services directly.")

    def _create_incident(self, session: ConversationSession, bystander_phone: str) -> Optional[dict]:
        """Create incident record in database."""
        try:
            # Generate incident number
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            incident_number = f"INC-{timestamp}"

            # Map breathing value
            breathing_val = session.get_data('breathing')
            patient_breathing = None
            if breathing_val == 'yes':
                patient_breathing = True
            elif breathing_val == 'no':
                patient_breathing = False

            # Map consciousness
            conscious_val = session.get_data('conscious')
            patient_conscious = None
            if conscious_val == 'yes':
                patient_conscious = True
            elif conscious_val == 'no':
                patient_conscious = False

            # Parse victim count
            victim_count_str = session.get_data('victim_count', '1')
            victim_count = 1
            if victim_count_str.startswith('4'):
                victim_count = 4
            elif victim_count_str.isdigit():
                victim_count = int(victim_count_str)

            incident_data = {
                'incident_number': incident_number,
                'member_id': session.get_data('member_uuid'),
                'emergency_type': session.get_data('emergency_type'),
                'patient_conscious': patient_conscious,
                'patient_breathing': patient_breathing,
                'victim_count': victim_count,
                'scene_description': session.get_data('scene_description'),
                'gps_latitude': session.get_data('latitude'),
                'gps_longitude': session.get_data('longitude'),
                'address_description': session.get_data('address'),
                'activated_by_phone': bystander_phone,
                'activation_method': 'whatsapp_chatbot',
                'status': 'activated',
                'activated_at': datetime.now().isoformat()
            }

            result = self.supabase.table('incidents').insert(incident_data).execute()
            return result.data[0] if result.data else None

        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            return None

    def _notify_next_of_kin(self, session: ConversationSession) -> None:
        """Notify next of kin about the emergency."""
        try:
            member_uuid = session.get_data('member_uuid')
            if not member_uuid:
                return

            # Get next of kin
            result = self.supabase.table('next_of_kin').select('*').eq(
                'member_id', member_uuid
            ).eq('is_primary', True).execute()

            if result.data:
                nok = result.data[0]
                nok_phone = nok.get('phone_number')

                if nok_phone:
                    messages.send_nok_alert(
                        to=nok_phone,
                        member_name=session.get_data('member_name'),
                        incident_number=session.get_data('incident_number'),
                        location_description=session.get_data('address')
                    )

        except Exception as e:
            logger.error(f"Error notifying next of kin: {e}")


class EmergencyHandler:
    """
    Main handler for emergency flow triggered by NFC/QR scan.

    NFC card URL format: wa.me/15550870762?text=EMERGENCY:LT-2025-A7X9K3
    """

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.emergency_flow = EmergencyFlowHandler(supabase_client)

    def get_member_by_id(self, member_id: str) -> Optional[dict]:
        """Look up member by member_id (LT-XXXX format)."""
        try:
            logger.info(f"Looking up member: {member_id}")
            result = self.supabase.table('members').select(
                '*, emr_records(*), subscriptions(*, tiers(*))'
            ).eq('member_id', member_id).execute()

            if result.data:
                logger.info(f"Member found: {result.data[0].get('first_name')}")
                return result.data[0]
            else:
                logger.warning(f"Member not found: {member_id}")
                return None

        except Exception as e:
            logger.error(f"Error looking up member: {e}")
            return None

    def handle_emergency_trigger(self, phone_number: str, member_id: str) -> dict:
        """
        Handle emergency trigger from NFC/QR scan.

        Triggered by: EMERGENCY:LT-2025-A7X9K3

        Args:
            phone_number: Bystander's phone number (who scanned the card)
            member_id: Member ID from the scanned card

        Returns:
            API response
        """
        logger.info(f"Emergency triggered for member {member_id} by {phone_number}")

        session = conversation_manager.get_session(phone_number)

        # Look up member
        member = self.get_member_by_id(member_id)

        if not member:
            logger.warning(f"Member not found: {member_id}")
            return messages.send_text(
                phone_number,
                f"*MEMBER NOT FOUND*\n\nID: {member_id}\n\nPlease verify the card and try again, or call emergency services directly:\n\n*MARS:* 0242 700991\n*Netstar:* 0772 390 303"
            )

        # Check subscription status
        subscriptions = member.get('subscriptions', [])
        active_sub = None
        for sub in subscriptions:
            if sub.get('status') == 'active':
                active_sub = sub
                break

        if not active_sub:
            # Member exists but subscription expired - still help but warn
            logger.warning(f"Subscription expired for member {member_id}")
            messages.send_text(
                phone_number,
                f"*SUBSCRIPTION EXPIRED*\n\n*Member:* {member.get('first_name')} {member.get('last_name')}\n\nEmergency services will still be dispatched, but coverage may not apply."
            )

        # Start emergency flow
        self.emergency_flow.start_emergency(session, member)
        return self.emergency_flow.send_initial_message(phone_number, session)

    def route_message(self, phone_number: str, message_type: str, message_data: dict) -> dict:
        """
        Route incoming WhatsApp messages.

        Only handles:
        1. EMERGENCY:LT-XXXX trigger from NFC scan
        2. Responses during active emergency flow (buttons, lists, location)
        """
        logger.info(f"Routing {message_type} message from {phone_number}")

        session = conversation_manager.get_session(phone_number)

        # Handle text messages
        if message_type == 'text':
            text = message_data.get('body', '').strip()
            logger.info(f"Text received: {text[:50]}...")

            # Check for emergency trigger (from NFC deep link)
            # Format: EMERGENCY:LT-2025-A7X9K3
            if text.upper().startswith('EMERGENCY:'):
                member_id = text.split(':', 1)[1].strip().upper()
                return self.handle_emergency_trigger(phone_number, member_id)

            # Direct member ID (backup)
            if text.upper().startswith('LT-'):
                return self.handle_emergency_trigger(phone_number, text.upper())

            # If in active emergency flow, handle text input (scene description)
            if session.state != ConversationState.IDLE:
                return self.emergency_flow.handle_input(session, phone_number, 'text', text)

            # Not in a flow and not an emergency trigger - ignore or send help
            logger.info(f"Ignoring non-emergency message from {phone_number}")
            return messages.send_text(
                phone_number,
                "*LifeTap Emergency Response*\n\nTo activate emergency services, tap the NFC card or scan QR code on a member's LifeTap card.\n\nFor support: support@lifetap.co.zw"
            )

        # Handle interactive responses (buttons, lists)
        elif message_type == 'interactive':
            interactive = message_data
            interactive_type = interactive.get('type')

            if session.state == ConversationState.IDLE:
                # Not in a flow - ignore
                logger.info(f"Ignoring interactive message - no active flow")
                return {'status': 'ignored'}

            if interactive_type == 'button_reply':
                button_id = interactive.get('button_reply', {}).get('id', '')
                logger.info(f"Button pressed: {button_id}")
                return self.emergency_flow.handle_input(session, phone_number, 'button', button_id)

            elif interactive_type == 'list_reply':
                list_id = interactive.get('list_reply', {}).get('id', '')
                logger.info(f"List selected: {list_id}")
                return self.emergency_flow.handle_input(session, phone_number, 'list', list_id)

        # Handle location
        elif message_type == 'location':
            location = message_data
            logger.info(f"Location received: {location.get('latitude')}, {location.get('longitude')}")

            if session.state != ConversationState.IDLE:
                return self.emergency_flow.handle_input(session, phone_number, 'location', location)

            # Location without active flow - ignore
            return {'status': 'ignored'}

        # Unknown message type
        logger.info(f"Unknown message type: {message_type}")
        return {'status': 'ignored'}


# Alias for backwards compatibility
MainMenuHandler = EmergencyHandler
