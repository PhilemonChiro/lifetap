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

import sys
from datetime import datetime
from typing import Optional, Dict, Any

from . import messages

# Simple print logging that goes to stdout (captured by Gunicorn)
def log(msg: str):
    """Print log message to stdout with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] CHATBOT: {msg}", flush=True)


# =============================================================================
# SIMPLE IN-MEMORY SESSION STORE
# =============================================================================

# Session storage: phone_number -> session_data
_sessions: Dict[str, Dict[str, Any]] = {}


def get_session(phone: str) -> Dict[str, Any]:
    """Get or create session for a phone number."""
    if phone not in _sessions:
        _sessions[phone] = {
            "state": "idle",
            "data": {},
            "member_id": None,
            "member_uuid": None,
            "member_name": None,
            "updated_at": datetime.now()
        }
        log(f"New session created for {phone}")
    return _sessions[phone]


def clear_session(phone: str):
    """Clear session for a phone number."""
    if phone in _sessions:
        del _sessions[phone]
        log(f"Session cleared for {phone}")


# =============================================================================
# MAIN MESSAGE HANDLER
# =============================================================================

class ChatbotHandler:
    """Simple synchronous chatbot handler."""

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        log("ChatbotHandler initialized")

    def handle_message(self, phone: str, msg_type: str, msg_data: Dict) -> Dict:
        """
        Main entry point for handling incoming messages.

        Args:
            phone: Sender phone number
            msg_type: Message type (text, interactive, location)
            msg_data: Message content

        Returns:
            Response dict with status
        """
        log(f"=== INCOMING MESSAGE ===")
        log(f"Phone: {phone}")
        log(f"Type: {msg_type}")
        log(f"Data: {msg_data}")

        session = get_session(phone)
        state = session["state"]
        log(f"Current state: {state}")

        try:
            # Route based on message type
            if msg_type == "text":
                return self._handle_text(phone, session, msg_data)
            elif msg_type == "interactive":
                return self._handle_interactive(phone, session, msg_data)
            elif msg_type == "location":
                return self._handle_location(phone, session, msg_data)
            else:
                log(f"Unknown message type: {msg_type}")
                return {"status": "ignored"}

        except Exception as e:
            log(f"ERROR handling message: {e}")
            import traceback
            traceback.print_exc()
            messages.send_text(phone, "Sorry, an error occurred. Please try again.")
            return {"status": "error", "error": str(e)}

    # =========================================================================
    # TEXT MESSAGE HANDLING
    # =========================================================================

    def _handle_text(self, phone: str, session: Dict, data: Dict) -> Dict:
        """Handle text messages."""
        text = data.get("body", "").strip()
        log(f"Text message: {text[:50]}...")

        # Check for emergency trigger
        if text.upper().startswith("EMERGENCY:"):
            member_id = text.split(":", 1)[1].strip().upper()
            log(f"Emergency trigger detected: {member_id}")
            return self._start_emergency(phone, session, member_id)

        # Direct member ID
        if text.upper().startswith("LT-"):
            log(f"Direct member ID: {text.upper()}")
            return self._start_emergency(phone, session, text.upper())

        # Handle scene description input (both scene and scene_input states)
        if session["state"] in ("scene", "scene_input"):
            return self._handle_scene_text(phone, session, text)

        # Default: send help
        log(f"No matching handler, sending help")
        messages.send_text(
            phone,
            "*LifeTap Emergency Response*\n\n"
            "To activate emergency services, tap the NFC card or scan QR code on a member's LifeTap card."
        )
        return {"status": "help_sent"}

    # =========================================================================
    # INTERACTIVE MESSAGE HANDLING
    # =========================================================================

    def _handle_interactive(self, phone: str, session: Dict, data: Dict) -> Dict:
        """Handle interactive messages (buttons, lists)."""
        log(f"Interactive message data: {data}")

        # Extract selection ID
        interactive_type = data.get("type", "")
        selection_id = ""

        if interactive_type == "button_reply":
            selection_id = data.get("button_reply", {}).get("id", "")
        elif interactive_type == "list_reply":
            selection_id = data.get("list_reply", {}).get("id", "")

        log(f"Interactive type: {interactive_type}, selection: {selection_id}")

        if not selection_id:
            log("No selection ID found")
            return {"status": "no_selection"}

        state = session["state"]
        log(f"Routing interactive for state: {state}")

        # Route based on state
        if state == "emergency_type":
            return self._handle_emergency_type(phone, session, selection_id)
        elif state == "conscious":
            return self._handle_conscious(phone, session, selection_id)
        elif state == "breathing":
            return self._handle_breathing(phone, session, selection_id)
        elif state == "victim_count":
            return self._handle_victim_count(phone, session, selection_id)
        elif state == "scene":
            return self._handle_scene_option(phone, session, selection_id)
        else:
            log(f"No handler for state {state}")
            return {"status": "ignored"}

    # =========================================================================
    # LOCATION HANDLING
    # =========================================================================

    def _handle_location(self, phone: str, session: Dict, data: Dict) -> Dict:
        """Handle location messages."""
        lat = data.get("latitude")
        lng = data.get("longitude")
        address = data.get("name") or data.get("address")

        log(f"Location received: {lat}, {lng}, {address}")

        if session["state"] == "location":
            return self._handle_location_received(phone, session, lat, lng, address)

        log("Location received but not in location state")
        return {"status": "ignored"}

    # =========================================================================
    # EMERGENCY FLOW
    # =========================================================================

    def _start_emergency(self, phone: str, session: Dict, member_id: str) -> Dict:
        """Start emergency flow for a member."""
        log(f"Starting emergency for member: {member_id}")

        # Look up member
        member = self._get_member(member_id)

        if not member:
            log(f"Member not found: {member_id}")
            messages.send_text(
                phone,
                f"*MEMBER NOT FOUND*\n\n"
                f"ID: {member_id}\n\n"
                f"Please verify the card and try again, or call emergency services directly:\n\n"
                f"*MARS:* 0242 700991\n"
                f"*Netstar:* 0772 390 303"
            )
            return {"status": "member_not_found"}

        # Store member info
        session["member_id"] = member_id
        session["member_uuid"] = member.get("id")
        session["member_name"] = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip()
        session["data"] = {}

        log(f"Member found: {session['member_name']}")

        # Get EMR data
        emr = member.get("emr_records") or {}
        if isinstance(emr, list) and emr:
            emr = emr[0]

        blood_type = emr.get("blood_type", "Unknown")
        allergies = ", ".join(emr.get("allergies", [])) or "None known"
        conditions = ", ".join(emr.get("chronic_conditions", [])) or "None known"

        # Get subscription tier
        subscriptions = member.get("subscriptions", [])
        active_sub = next((s for s in subscriptions if s.get("status") == "active"), None)

        if active_sub:
            tier_info = active_sub.get("tiers", {})
            session["data"]["member_tier"] = tier_info.get("name", "lifeline") if tier_info else "lifeline"
        else:
            session["data"]["member_tier"] = None
            messages.send_text(
                phone,
                f"*SUBSCRIPTION EXPIRED*\n\n"
                f"*Member:* {session['member_name']}\n\n"
                f"Emergency services will still be dispatched, but coverage may not apply."
            )

        # Send header with medical info
        messages.send_emergency_header(
            to=phone,
            member_name=session["member_name"],
            member_id=member_id,
            blood_type=blood_type,
            allergies=allergies,
            conditions=conditions
        )

        # Move to emergency type selection
        session["state"] = "emergency_type"
        log(f"State changed to: emergency_type")
        messages.send_emergency_type_list(phone)

        return {"status": "started"}

    def _handle_emergency_type(self, phone: str, session: Dict, selection: str) -> Dict:
        """Handle emergency type selection."""
        log(f"Emergency type selected: {selection}")

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

        session["data"]["emergency_type"] = emergency_types.get(selection, selection)
        session["data"]["emergency_type_id"] = selection
        session["state"] = "conscious"

        log(f"State changed to: conscious")
        messages.send_conscious_buttons(phone)

        return {"status": "ok"}

    def _handle_conscious(self, phone: str, session: Dict, selection: str) -> Dict:
        """Handle consciousness selection."""
        log(f"Conscious selected: {selection}")

        conscious_map = {
            "conscious_yes": "yes",
            "conscious_no": "no",
            "conscious_unsure": "unsure"
        }

        session["data"]["conscious"] = conscious_map.get(selection, selection)
        session["state"] = "breathing"

        log(f"State changed to: breathing")
        messages.send_breathing_buttons(phone)

        return {"status": "ok"}

    def _handle_breathing(self, phone: str, session: Dict, selection: str) -> Dict:
        """Handle breathing selection."""
        log(f"Breathing selected: {selection}")

        breathing_map = {
            "breathing_yes": "yes",
            "breathing_struggling": "struggling",
            "breathing_no": "no"
        }

        session["data"]["breathing"] = breathing_map.get(selection, selection)
        session["state"] = "victim_count"

        log(f"State changed to: victim_count")
        messages.send_victim_count_list(phone)

        return {"status": "ok"}

    def _handle_victim_count(self, phone: str, session: Dict, selection: str) -> Dict:
        """Handle victim count selection."""
        log(f"Victim count selected: {selection}")

        count_map = {
            "victims_1": "1",
            "victims_2": "2",
            "victims_3": "3",
            "victims_4plus": "4+"
        }

        session["data"]["victim_count"] = count_map.get(selection, "1")
        session["state"] = "scene"

        log(f"State changed to: scene")
        messages.send_scene_description_request(phone)

        return {"status": "ok"}

    def _handle_scene_option(self, phone: str, session: Dict, selection: str) -> Dict:
        """Handle scene description option."""
        log(f"Scene option selected: {selection}")

        if selection == "scene_skip":
            session["data"]["scene_description"] = None
            session["state"] = "location"
            log(f"State changed to: location")
            messages.send_location_request_emergency(phone)
        elif selection == "scene_describe":
            session["state"] = "scene_input"
            log(f"State changed to: scene_input")
            messages.send_text(phone, "Please describe the scene briefly:")

        return {"status": "ok"}

    def _handle_scene_text(self, phone: str, session: Dict, text: str) -> Dict:
        """Handle scene description text input."""
        log(f"Scene description: {text[:50]}...")

        session["data"]["scene_description"] = text
        session["state"] = "location"

        log(f"State changed to: location")
        messages.send_location_request_emergency(phone)

        return {"status": "ok"}

    def _handle_location_received(self, phone: str, session: Dict, lat: float, lng: float, address: str) -> Dict:
        """Handle location and create incident."""
        log(f"Creating incident with location: {lat}, {lng}")

        session["data"]["latitude"] = lat
        session["data"]["longitude"] = lng
        session["data"]["address"] = address

        # Create incident
        incident = self._create_incident(phone, session)

        if incident:
            incident_number = incident.get("incident_number")
            log(f"Incident created: {incident_number}")

            # Send confirmation
            messages.send_emergency_confirmed(
                to=phone,
                incident_number=incident_number,
                member_name=session["member_name"]
            )

            # Send first aid guidance
            emergency_type_id = session["data"].get("emergency_type_id", "other")
            messages.send_first_aid_guidance(phone, emergency_type_id)

            # Send help on way
            messages.send_help_on_way(
                to=phone,
                incident_number=incident_number,
                member_name=session["member_name"]
            )

            # Notify next of kin
            self._notify_next_of_kin(session)

            # Clear session
            clear_session(phone)

            return {"status": "completed", "incident_number": incident_number}
        else:
            log("Failed to create incident")
            messages.send_text(
                phone,
                "*ERROR*\n\n"
                "Failed to register emergency. Please call emergency services directly:\n\n"
                "*MARS:* 0242 700991\n"
                "*Netstar:* 0772 390 303"
            )
            return {"status": "error"}

    # =========================================================================
    # DATABASE HELPERS
    # =========================================================================

    def _get_member(self, member_id: str) -> Optional[Dict]:
        """Look up member by member_id."""
        try:
            result = self.supabase.table("members").select(
                "*, emr_records(*), subscriptions(*, tiers(*))"
            ).eq("member_id", member_id).execute()

            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            log(f"Error fetching member: {e}")
            return None

    def _create_incident(self, phone: str, session: Dict) -> Optional[Dict]:
        """Create incident in database."""
        try:
            data = session["data"]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            incident_number = f"INC-{timestamp}"

            # Map values
            breathing = data.get("breathing")
            patient_breathing = True if breathing == "yes" else (False if breathing == "no" else None)

            conscious = data.get("conscious")
            patient_conscious = True if conscious == "yes" else (False if conscious == "no" else None)

            victim_count_str = data.get("victim_count", "1")
            victim_count = 4 if victim_count_str.startswith("4") else int(victim_count_str) if victim_count_str.isdigit() else 1

            incident_data = {
                "incident_number": incident_number,
                "member_id": session["member_uuid"],
                "member_tier": data.get("member_tier"),
                "emergency_type": data.get("emergency_type_id"),
                "patient_conscious": patient_conscious,
                "patient_breathing": patient_breathing,
                "victim_count": victim_count,
                "scene_description": data.get("scene_description"),
                "gps_latitude": data.get("latitude"),
                "gps_longitude": data.get("longitude"),
                "address_description": data.get("address"),
                "activated_by_phone": phone,
                "activation_method": "whatsapp",
                "status": "activated",
                "activated_at": datetime.now().isoformat()
            }

            log(f"Inserting incident: {incident_data}")
            result = self.supabase.table("incidents").insert(incident_data).execute()

            if result.data:
                return result.data[0]
            return None

        except Exception as e:
            log(f"Error creating incident: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _notify_next_of_kin(self, session: Dict):
        """Notify next of kin about emergency."""
        try:
            member_uuid = session["member_uuid"]
            if not member_uuid:
                return

            result = self.supabase.table("next_of_kin").select("*").eq(
                "member_id", member_uuid
            ).eq("is_primary", True).execute()

            if result.data:
                nok = result.data[0]
                nok_phone = nok.get("phone_number")

                if nok_phone:
                    messages.send_nok_alert(
                        to=nok_phone,
                        member_name=session["member_name"],
                        incident_number=session["data"].get("incident_number", ""),
                        location_description=session["data"].get("address")
                    )
                    log(f"NOK notified: {nok_phone}")
        except Exception as e:
            log(f"Error notifying NOK: {e}")
