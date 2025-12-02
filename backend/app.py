"""
LifeTap Backend Application
Main Flask application with all routes and integrations.
"""

import os
import json
import base64
import hashlib
import requests
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, g
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', 'dev-secret-key')

# =============================================================================
# SUPABASE CLIENT
# =============================================================================

supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# =============================================================================
# WHATSAPP CONFIGURATION
# =============================================================================

WHATSAPP_CONFIG = {
    'api_version': 'v18.0',
    'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
    'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN'),
    'webhook_verify_token': os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN'),
}

# Private key for Flow decryption
private_key = None


def load_private_key():
    """
    Load RSA private key for WhatsApp Flow decryption.

    Supports two methods:
    1. WHATSAPP_PRIVATE_KEY env var (base64 encoded PEM) - for Coolify secrets
    2. WHATSAPP_PRIVATE_KEY_PATH file path - for local development
    """
    global private_key
    key_password = os.getenv('WHATSAPP_PRIVATE_KEY_PASSWORD')
    password_bytes = key_password.encode() if key_password else None

    try:
        # Method 1: Load from environment variable (Coolify secrets)
        key_env = os.getenv('WHATSAPP_PRIVATE_KEY')
        if key_env:
            # Key can be base64 encoded or raw PEM
            try:
                key_bytes = base64.b64decode(key_env)
            except Exception:
                key_bytes = key_env.encode()

            private_key = serialization.load_pem_private_key(
                key_bytes,
                password=password_bytes,
                backend=default_backend()
            )
            app.logger.info("Private key loaded from environment variable")
            return

        # Method 2: Load from file path
        key_path = os.getenv('WHATSAPP_PRIVATE_KEY_PATH', 'keys/private.pem')
        with open(key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password_bytes,
                backend=default_backend()
            )
        app.logger.info(f"Private key loaded from file: {key_path}")

    except FileNotFoundError:
        app.logger.error(f"Private key file not found. Set WHATSAPP_PRIVATE_KEY env var or check path.")
    except Exception as e:
        app.logger.error(f"Failed to load private key: {e}")


# =============================================================================
# ENCRYPTION / DECRYPTION HELPERS
# =============================================================================

def decrypt_flow_request(encrypted_flow_data: str, encrypted_aes_key: str, initial_vector: str) -> dict:
    """Decrypt WhatsApp Flow request."""
    global private_key

    if private_key is None:
        load_private_key()

    # Decode base64
    encrypted_aes_key_bytes = base64.b64decode(encrypted_aes_key)
    iv_bytes = base64.b64decode(initial_vector)
    encrypted_data_bytes = base64.b64decode(encrypted_flow_data)

    # Decrypt AES key with RSA-OAEP
    aes_key = private_key.decrypt(
        encrypted_aes_key_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt payload with AES-GCM
    aesgcm = AESGCM(aes_key)
    decrypted = aesgcm.decrypt(iv_bytes, encrypted_data_bytes, None)

    # Store for response encryption
    g.aes_key = aes_key
    g.iv = iv_bytes

    return json.loads(decrypted.decode('utf-8'))


def encrypt_flow_response(response: dict) -> str:
    """Encrypt WhatsApp Flow response."""
    aes_key = g.aes_key
    iv = g.iv

    # Flip IV for response
    flipped_iv = bytes(~b & 0xFF for b in iv)

    aesgcm = AESGCM(aes_key)
    encrypted = aesgcm.encrypt(flipped_iv, json.dumps(response).encode(), None)

    return base64.b64encode(encrypted).decode('utf-8')


# =============================================================================
# WHATSAPP API HELPERS
# =============================================================================

def send_whatsapp_message(to: str, message: str):
    """Send a text message via WhatsApp Graph API."""
    url = f"https://graph.facebook.com/{WHATSAPP_CONFIG['api_version']}/{WHATSAPP_CONFIG['phone_number_id']}/messages"

    headers = {
        'Authorization': f"Bearer {WHATSAPP_CONFIG['access_token']}",
        'Content-Type': 'application/json'
    }

    payload = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': message}
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def send_location_request(to: str, member_name: str):
    """Send interactive message requesting location."""
    url = f"https://graph.facebook.com/{WHATSAPP_CONFIG['api_version']}/{WHATSAPP_CONFIG['phone_number_id']}/messages"

    headers = {
        'Authorization': f"Bearer {WHATSAPP_CONFIG['access_token']}",
        'Content-Type': 'application/json'
    }

    payload = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'interactive',
        'interactive': {
            'type': 'button',
            'body': {
                'text': f"🚨 Emergency registered for {member_name}.\n\n📍 Please share your current location so we can dispatch an ambulance immediately.\n\nTap the button below or use the 📎 attachment icon to share location."
            },
            'action': {
                'buttons': [
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'share_location',
                            'title': '📍 Share Location'
                        }
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def send_ambulance_dispatched(to: str, incident: dict, ambulance: dict):
    """Send ambulance dispatched confirmation."""
    message = f"""✅ AMBULANCE DISPATCHED

🕐 ETA: {ambulance.get('eta_minutes', 'N/A')} minutes

🚑 Vehicle: {ambulance.get('vehicle_reg', 'N/A')}
👤 Driver: {ambulance.get('driver_name', 'N/A')}
📞 Contact: {ambulance.get('driver_phone', 'N/A')}

📍 Track: https://lifetap.co.zw/t/{incident.get('incident_number')}

Stay with the patient. Help is on the way."""

    return send_whatsapp_message(to, message)


def notify_next_of_kin(nok_phone: str, member_name: str, incident: dict):
    """Send emergency alert to Next of Kin."""
    message = f"""🚨 EMERGENCY ALERT

{member_name} has had an emergency.

📍 Location: {incident.get('address', 'Location being determined')}
🚑 Ambulance ETA: {incident.get('eta_minutes', 'Dispatching...')} minutes

📍 Track live: https://lifetap.co.zw/t/{incident.get('incident_number')}

We will keep you updated."""

    return send_whatsapp_message(nok_phone, message)


# =============================================================================
# DATABASE HELPERS
# =============================================================================

def get_member_by_id(member_id: str) -> dict:
    """Fetch member from Supabase."""
    try:
        result = supabase.table('members').select(
            '*, emr_records(*), next_of_kin(*)'
        ).eq('member_id', member_id).single().execute()

        return result.data
    except Exception as e:
        app.logger.error(f"Error fetching member {member_id}: {e}")
        return None


def create_incident(data: dict) -> dict:
    """Create emergency incident in Supabase."""
    try:
        # Generate incident number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        incident_number = f"INC-{timestamp}"

        incident_data = {
            'incident_number': incident_number,
            'member_id': data.get('member_id'),
            'emergency_type': data.get('emergency_type'),
            'patient_conscious': data.get('conscious'),
            'patient_breathing': data.get('breathing'),
            'victim_count': data.get('victim_count'),
            'scene_description': data.get('scene_description'),
            'activated_by_phone': data.get('bystander_phone'),
            'status': 'activated',
            'activated_at': datetime.now().isoformat()
        }

        result = supabase.table('incidents').insert(incident_data).execute()
        return result.data[0] if result.data else None

    except Exception as e:
        app.logger.error(f"Error creating incident: {e}")
        return None


def update_incident_location(incident_id: str, lat: float, lng: float, address: str = None):
    """Update incident with GPS location."""
    try:
        supabase.table('incidents').update({
            'gps_latitude': lat,
            'gps_longitude': lng,
            'address_description': address,
            'status': 'location_received'
        }).eq('id', incident_id).execute()
    except Exception as e:
        app.logger.error(f"Error updating incident location: {e}")


# =============================================================================
# WHATSAPP FLOW ENDPOINT
# =============================================================================

@app.route('/whatsapp/flow', methods=['POST'])
def handle_flow():
    """Handle encrypted WhatsApp Flow requests."""
    try:
        data = request.get_json()

        # Decrypt request
        flow_data = decrypt_flow_request(
            data.get('encrypted_flow_data'),
            data.get('encrypted_aes_key'),
            data.get('initial_vector')
        )

        app.logger.info(f"Flow request: {json.dumps(flow_data, indent=2)}")

        action = flow_data.get('action')
        screen = flow_data.get('screen')
        version = flow_data.get('version')
        flow_token = flow_data.get('flow_token')

        # Handle different actions
        if action == 'ping':
            response = {'version': version, 'data': {'status': 'active'}}

        elif action == 'INIT':
            # Extract member ID from flow token
            member_id = flow_token.split(':')[-1] if ':' in flow_token else flow_token

            # Get member data
            member = get_member_by_id(member_id)

            if member:
                emr = member.get('emr_records', {}) or {}
                response = {
                    'version': version,
                    'screen': 'EMERGENCY_SCREEN',
                    'data': {
                        'member_name': f"{member.get('first_name', '')} {member.get('last_name', '')}".strip() or 'Unknown',
                        'member_id': member_id,
                        'blood_type': emr.get('blood_type', 'Unknown'),
                        'allergies': ', '.join(emr.get('allergies', [])) or 'None known',
                        'conditions': ', '.join(emr.get('chronic_conditions', [])) or 'None known'
                    }
                }
            else:
                response = {
                    'version': version,
                    'screen': 'EMERGENCY_SCREEN',
                    'data': {
                        'member_name': 'Unknown Member',
                        'member_id': member_id,
                        'blood_type': 'Unknown',
                        'allergies': 'Unknown',
                        'conditions': 'Unknown'
                    }
                }

        elif action == 'data_exchange':
            # User submitted emergency form
            payload = flow_data.get('data', {})

            # Create incident
            incident = create_incident({
                'member_id': payload.get('member_id'),
                'emergency_type': payload.get('emergency_type'),
                'conscious': payload.get('conscious'),
                'breathing': payload.get('breathing'),
                'victim_count': payload.get('victim_count'),
                'scene_description': payload.get('scene_description'),
                'bystander_phone': flow_data.get('flow_token')  # Contains phone
            })

            # Store incident ID for follow-up
            incident_id = incident.get('id') if incident else None

            response = {
                'version': version,
                'screen': 'SUCCESS',
                'data': {
                    'extension_message_response': {
                        'params': {
                            'incident_id': incident_id
                        }
                    }
                }
            }

        else:
            response = {
                'version': version,
                'screen': 'EMERGENCY_SCREEN',
                'data': {}
            }

        # Encrypt and return
        encrypted = encrypt_flow_response(response)
        return jsonify({'encrypted_response': encrypted})

    except Exception as e:
        app.logger.error(f"Flow error: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# WHATSAPP WEBHOOK (for regular messages)
# =============================================================================

@app.route('/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == WHATSAPP_CONFIG['webhook_verify_token']:
        return challenge, 200

    return 'Forbidden', 403


@app.route('/whatsapp/webhook', methods=['POST'])
def receive_webhook():
    """Receive WhatsApp messages and events."""
    data = request.get_json()

    app.logger.info(f"Webhook received: {json.dumps(data, indent=2)}")

    try:
        # Extract message info
        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])

        for message in messages:
            msg_type = message.get('type')
            from_number = message.get('from')

            if msg_type == 'location':
                # Received location from bystander
                location = message.get('location', {})
                lat = location.get('latitude')
                lng = location.get('longitude')

                app.logger.info(f"Location received: {lat}, {lng} from {from_number}")

                # TODO: Find the active incident for this phone number
                # Update incident with location
                # Dispatch ambulance

                # Send confirmation
                send_whatsapp_message(
                    from_number,
                    "📍 Location received! Dispatching nearest ambulance now..."
                )

            elif msg_type == 'text':
                text = message.get('text', {}).get('body', '')

                # Check for emergency trigger from NFC/QR
                if text.startswith('EMERGENCY:'):
                    member_id = text.replace('EMERGENCY:', '').strip()
                    app.logger.info(f"Emergency triggered for {member_id}")

                    # TODO: Send Flow or interactive message

            elif msg_type == 'interactive':
                # Button click response
                interactive = message.get('interactive', {})
                button_id = interactive.get('button_reply', {}).get('id')

                if button_id == 'share_location':
                    send_whatsapp_message(
                        from_number,
                        "Please tap the 📎 attachment icon, select 'Location', and share your current location."
                    )

    except Exception as e:
        app.logger.error(f"Webhook processing error: {e}")

    return jsonify({'status': 'ok'}), 200


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'lifetap-backend'
    })


# =============================================================================
# RUN
# =============================================================================

if __name__ == '__main__':
    load_private_key()
    app.run(host='0.0.0.0', port=5000, debug=True)
