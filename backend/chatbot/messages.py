"""
WhatsApp Interactive Message Builders

Provides helper functions to construct WhatsApp Cloud API message payloads
for interactive messages (buttons, lists, location requests).
"""

import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

WHATSAPP_API_VERSION = 'v18.0'


def get_api_url() -> str:
    """Get WhatsApp Graph API URL."""
    phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    return f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_id}/messages"


def get_headers() -> dict:
    """Get API headers."""
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    return {
        'Authorization': f"Bearer {token}",
        'Content-Type': 'application/json'
    }


def send_message(payload: dict) -> dict:
    """Send message to WhatsApp API."""
    url = get_api_url()
    headers = get_headers()

    logger.info(f"Sending message to: {payload.get('to')}")
    logger.debug(f"Payload: {payload}")

    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        if response.status_code != 200:
            logger.error(f"WhatsApp API error: {response.status_code} - {result}")
        else:
            logger.info(f"Message sent successfully: {result.get('messages', [{}])[0].get('id', 'unknown')}")

        return result
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return {'error': str(e)}


def send_text(to: str, text: str, preview_url: bool = False) -> dict:
    """Send a simple text message."""
    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to,
        'type': 'text',
        'text': {
            'preview_url': preview_url,
            'body': text
        }
    }
    return send_message(payload)


def send_buttons(to: str, body: str, buttons: list[dict], header: str = None, footer: str = None) -> dict:
    """
    Send interactive button message (max 3 buttons).

    buttons format: [{'id': 'btn_1', 'title': 'Button 1'}, ...]
    """
    interactive = {
        'type': 'button',
        'body': {'text': body},
        'action': {
            'buttons': [
                {
                    'type': 'reply',
                    'reply': {'id': btn['id'], 'title': btn['title'][:20]}  # Max 20 chars
                }
                for btn in buttons[:3]  # Max 3 buttons
            ]
        }
    }

    if header:
        interactive['header'] = {'type': 'text', 'text': header}

    if footer:
        interactive['footer'] = {'text': footer}

    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to,
        'type': 'interactive',
        'interactive': interactive
    }
    return send_message(payload)


def send_list(to: str, body: str, button_text: str, sections: list[dict], header: str = None, footer: str = None) -> dict:
    """
    Send interactive list message.

    sections format:
    [
        {
            'title': 'Section 1',
            'rows': [
                {'id': 'row_1', 'title': 'Row 1', 'description': 'Description'}
            ]
        }
    ]
    """
    interactive = {
        'type': 'list',
        'body': {'text': body},
        'action': {
            'button': button_text[:20],  # Max 20 chars
            'sections': sections
        }
    }

    if header:
        interactive['header'] = {'type': 'text', 'text': header}

    if footer:
        interactive['footer'] = {'text': footer}

    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to,
        'type': 'interactive',
        'interactive': interactive
    }
    return send_message(payload)


def send_location_request(to: str, body: str) -> dict:
    """
    Send location request message.
    User will see a button to share their location.
    """
    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to,
        'type': 'interactive',
        'interactive': {
            'type': 'location_request_message',
            'body': {'text': body},
            'action': {'name': 'send_location'}
        }
    }
    return send_message(payload)


def send_location(to: str, latitude: float, longitude: float, name: str = None, address: str = None) -> dict:
    """Send a location message."""
    location = {
        'latitude': latitude,
        'longitude': longitude
    }
    if name:
        location['name'] = name
    if address:
        location['address'] = address

    payload = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': to,
        'type': 'location',
        'location': location
    }
    return send_message(payload)


# =============================================================================
# EMERGENCY FLOW MESSAGES
# =============================================================================

def send_emergency_header(to: str, member_name: str, member_id: str, blood_type: str, allergies: str, conditions: str) -> dict:
    """Send emergency header with member info."""
    text = f"""*EMERGENCY ACTIVATED*

*Member:* {member_name}
*ID:* {member_id}

*Blood Type:* {blood_type}
*Allergies:* {allergies}
*Conditions:* {conditions}

Please answer the following questions to help us dispatch emergency services."""

    return send_text(to, text)


def send_emergency_type_list(to: str) -> dict:
    """Send emergency type selection list."""
    sections = [
        {
            'title': 'Emergency Type',
            'rows': [
                {'id': 'road_accident', 'title': 'Road Accident', 'description': 'Vehicle collision or road incident'},
                {'id': 'collapse', 'title': 'Person Collapsed', 'description': 'Sudden loss of consciousness'},
                {'id': 'heart_attack', 'title': 'Chest Pain', 'description': 'Heart attack or cardiac emergency'},
                {'id': 'breathing', 'title': 'Breathing Difficulty', 'description': 'Respiratory distress'},
                {'id': 'injury', 'title': 'Serious Injury', 'description': 'Severe bleeding or trauma'},
                {'id': 'seizure', 'title': 'Seizure', 'description': 'Convulsion or epileptic episode'},
                {'id': 'burn', 'title': 'Burn', 'description': 'Fire or chemical burn'},
                {'id': 'other', 'title': 'Other Emergency', 'description': 'Other medical emergency'}
            ]
        }
    ]

    return send_list(
        to=to,
        body="What type of emergency is this?",
        button_text="Select Emergency",
        sections=sections,
        header="What happened?"
    )


def send_conscious_buttons(to: str) -> dict:
    """Send consciousness status buttons."""
    buttons = [
        {'id': 'conscious_yes', 'title': 'Yes - Responsive'},
        {'id': 'conscious_no', 'title': 'No - Unconscious'},
        {'id': 'conscious_unsure', 'title': 'Not Sure'}
    ]

    return send_buttons(
        to=to,
        body="Is the person conscious and responsive?",
        buttons=buttons,
        header="Consciousness Check"
    )


def send_breathing_buttons(to: str) -> dict:
    """Send breathing status buttons."""
    buttons = [
        {'id': 'breathing_yes', 'title': 'Yes - Normal'},
        {'id': 'breathing_struggling', 'title': 'Yes - Struggling'},
        {'id': 'breathing_no', 'title': 'No'}
    ]

    return send_buttons(
        to=to,
        body="Is the person breathing?",
        buttons=buttons,
        header="Breathing Check"
    )


def send_victim_count_list(to: str) -> dict:
    """Send victim count selection."""
    sections = [
        {
            'title': 'Number of Victims',
            'rows': [
                {'id': 'victims_1', 'title': '1 person', 'description': 'Single victim'},
                {'id': 'victims_2', 'title': '2 people', 'description': 'Two victims'},
                {'id': 'victims_3', 'title': '3 people', 'description': 'Three victims'},
                {'id': 'victims_4plus', 'title': '4 or more', 'description': 'Multiple casualties'}
            ]
        }
    ]

    return send_list(
        to=to,
        body="How many people need emergency help?",
        button_text="Select Count",
        sections=sections,
        header="Victim Count"
    )


def send_scene_description_request(to: str) -> dict:
    """Ask for optional scene description."""
    buttons = [
        {'id': 'scene_skip', 'title': 'Skip'},
        {'id': 'scene_describe', 'title': 'Add Details'}
    ]

    return send_buttons(
        to=to,
        body="Would you like to add any details about the scene that could help responders?\n\n(e.g., exact location landmarks, hazards, number of vehicles involved)",
        buttons=buttons,
        header="Scene Details (Optional)"
    )


def send_location_request_emergency(to: str) -> dict:
    """Request location for emergency dispatch."""
    return send_location_request(
        to=to,
        body="*IMPORTANT: Share your location now*\n\nTap the button below to share your current GPS location so we can dispatch the nearest ambulance immediately.\n\nThis is required to send help to you."
    )


def send_emergency_confirmed(to: str, incident_number: str, member_name: str) -> dict:
    """Send emergency confirmation message."""
    text = f"""*EMERGENCY REGISTERED*

*Incident #:* {incident_number}
*Patient:* {member_name}

*Status:* Dispatching nearest ambulance

We are processing your emergency request. An ambulance will be dispatched to your location shortly.

*Next Steps:*
1. Stay on the line
2. Keep the patient calm
3. Do not move the patient unless in danger
4. Wait for ambulance crew instructions

*Track live:* https://lifetap.co.zw/t/{incident_number}"""

    return send_text(to, text)


def send_ambulance_eta(to: str, eta_minutes: int, vehicle_reg: str, driver_name: str, driver_phone: str, incident_number: str) -> dict:
    """Send ambulance ETA notification."""
    text = f"""*AMBULANCE DISPATCHED*

*ETA:* {eta_minutes} minutes

*Vehicle:* {vehicle_reg}
*Paramedic:* {driver_name}
*Contact:* {driver_phone}

*Track live:* https://lifetap.co.zw/t/{incident_number}

Stay with the patient. Help is on the way."""

    return send_text(to, text)


def send_nok_alert(to: str, member_name: str, incident_number: str, location_description: str = None) -> dict:
    """Send alert to next of kin."""
    location_text = f"\n*Location:* {location_description}" if location_description else ""

    text = f"""*EMERGENCY ALERT*

{member_name} has had a medical emergency and an ambulance has been dispatched.
{location_text}

*Track live:* https://lifetap.co.zw/t/{incident_number}

We will keep you updated on the status."""

    return send_text(to, text)


# =============================================================================
# FIRST AID GUIDANCE MESSAGES
# =============================================================================

FIRST_AID_GUIDES = {
    'road_accident': """*FIRST AID: Road Accident*

*DO:*
1. Ensure the scene is safe - check for traffic, fire, fuel leaks
2. Turn off vehicle ignitions if safe
3. Call for help if you haven't already
4. If victim is conscious, reassure them help is coming
5. Control bleeding with clean cloth and direct pressure
6. Keep victim still and warm with blanket/jacket

*DON'T:*
- Move the victim unless there's immediate danger (fire, traffic)
- Remove helmet if motorcyclist
- Give food or water
- Pull victim from vehicle

*If unconscious but breathing:* Place in recovery position (on side)""",

    'collapse': """*FIRST AID: Person Collapsed*

*Check responsiveness:*
1. Tap shoulders firmly and shout "Are you okay?"
2. If no response, check breathing (look, listen, feel for 10 seconds)

*If NOT breathing:*
Start CPR immediately:
1. Place heel of hand on center of chest
2. Push hard and fast (100-120 compressions/min)
3. Push down at least 5cm (2 inches)
4. Allow chest to fully rise between compressions
5. Continue until help arrives

*If breathing:*
1. Place in recovery position (on their side)
2. Monitor breathing continuously
3. Keep them warm""",

    'heart_attack': """*FIRST AID: Chest Pain / Heart Attack*

*Signs:* Crushing chest pain, pain spreading to arm/jaw/back, sweating, nausea

*DO:*
1. Help person sit in comfortable position (often semi-upright)
2. Loosen tight clothing
3. If person has prescribed aspirin, help them take it
4. If person has GTN spray, help them use it
5. Stay calm and reassure them
6. Monitor breathing and consciousness

*If person becomes unconscious and stops breathing:*
Start CPR immediately

*Keep person calm* - anxiety worsens the condition""",

    'breathing': """*FIRST AID: Breathing Difficulty*

*DO:*
1. Help person sit upright - this makes breathing easier
2. Loosen any tight clothing around neck and chest
3. If person has inhaler (asthma), help them use it
4. Open windows for fresh air
5. Encourage slow, deep breaths
6. Stay calm - panic worsens breathing

*If person has severe allergic reaction (swelling, hives):*
- Help them use EpiPen if available
- This is life-threatening - reassure help is coming

*If breathing stops:* Start CPR immediately""",

    'injury': """*FIRST AID: Serious Injury / Bleeding*

*For severe bleeding:*
1. Apply firm, direct pressure with clean cloth
2. Don't remove the cloth - add more on top if soaked
3. Elevate injured limb above heart if possible
4. Apply pressure to wound for at least 10 minutes
5. If wound has object embedded, don't remove it

*For broken bones:*
1. Don't move the injured area
2. Support the limb in position found
3. Apply ice wrapped in cloth if available
4. Watch for signs of shock (pale, cold, sweaty)

*Keep victim still and warm*""",

    'seizure': """*FIRST AID: Seizure / Convulsion*

*DO:*
1. Clear area of dangerous objects
2. Cushion their head with soft item
3. Time the seizure
4. Place in recovery position AFTER seizure stops
5. Stay with them until fully recovered

*DON'T:*
- Restrain the person
- Put anything in their mouth
- Give food or water until fully alert
- Move them unless in danger

*Call for help if:*
- Seizure lasts more than 5 minutes
- Person doesn't regain consciousness
- Person is injured
- It's their first seizure""",

    'burn': """*FIRST AID: Burns*

*For thermal burns (fire, hot liquid):*
1. Cool burn under cool running water for 20 minutes
2. Remove jewelry/clothing near burn (not if stuck)
3. Cover with clean, non-fluffy material (cling film is ideal)
4. Don't apply creams, butter, or ice
5. Don't burst blisters

*For chemical burns:*
1. Remove contaminated clothing carefully
2. Brush off dry chemicals before washing
3. Flush with water for at least 20 minutes

*For electrical burns:*
1. Don't touch person until power is off
2. Check for breathing and pulse
3. Treat visible burns as above""",

    'other': """*FIRST AID: General Guidelines*

*Stay calm and assess:*
1. Check if scene is safe for you
2. Check victim's responsiveness
3. Check breathing

*If conscious:*
1. Reassure them help is coming
2. Keep them comfortable and still
3. Keep them warm with blanket/jacket
4. Don't give food or water

*If unconscious but breathing:*
1. Place in recovery position (on side)
2. Monitor breathing continuously

*If not breathing:*
1. Start CPR: 30 chest compressions, 2 rescue breaths
2. Continue until help arrives

*Help is on the way - you're doing great!*"""
}


def send_first_aid_guidance(to: str, emergency_type: str) -> dict:
    """Send first aid guidance based on emergency type."""
    guide = FIRST_AID_GUIDES.get(emergency_type, FIRST_AID_GUIDES['other'])
    return send_text(to, guide)


def send_help_on_way(to: str, incident_number: str, member_name: str) -> dict:
    """Send help is on the way message with tracking link."""
    text = f"""*HELP IS ON THE WAY*

*Incident:* {incident_number}
*Patient:* {member_name}

An ambulance has been dispatched to your location.

*While you wait:*
1. Stay with the patient
2. Keep them calm and comfortable
3. Follow the first aid guidance above
4. Watch for any changes in condition

*Track ambulance live:*
https://lifetap.co.zw/t/{incident_number}

*Emergency contacts:*
MARS: 0242 700991
Netstar: 0772 390 303"""

    return send_text(to, text)


