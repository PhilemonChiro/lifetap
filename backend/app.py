"""
LifeTap Backend Application
Main Flask application with all routes and integrations.
"""

import os
import json
import base64
import hashlib
import requests
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, g
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from supabase import create_client, Client
from paynow import Paynow

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

# =============================================================================
# SMS GATEWAY CONFIGURATION (Android SMS Gateway - Cloud Mode)
# https://github.com/capcom6/android-sms-gateway
# =============================================================================

SMS_GATEWAY_CONFIG = {
    'base_url': os.getenv('SMS_GATEWAY_URL', 'https://api.sms-gate.app'),
    'username': os.getenv('SMS_GATEWAY_USERNAME'),
    'password': os.getenv('SMS_GATEWAY_PASSWORD'),
    'device_id': os.getenv('SMS_GATEWAY_DEVICE_ID'),
}

# =============================================================================
# PAYNOW CONFIGURATION
# =============================================================================

PAYNOW_CONFIG = {
    'integration_id': os.getenv('PAYNOW_INTEGRATION_ID'),
    'integration_key': os.getenv('PAYNOW_INTEGRATION_KEY'),
    'result_url': os.getenv('PAYNOW_RESULT_URL'),
    'return_url': os.getenv('PAYNOW_RETURN_URL'),
}

# Initialize Paynow client
paynow = None
if PAYNOW_CONFIG['integration_id'] and PAYNOW_CONFIG['integration_key']:
    paynow = Paynow(
        PAYNOW_CONFIG['integration_id'],
        PAYNOW_CONFIG['integration_key'],
        PAYNOW_CONFIG['result_url'],
        PAYNOW_CONFIG['return_url']
    )

# =============================================================================
# TIER HELPERS (fetch from database)
# =============================================================================

_tiers_cache = None
_tiers_cache_time = None
TIER_CACHE_TTL = 300  # Cache tiers for 5 minutes


def get_tiers() -> dict:
    """Fetch tiers from database with caching."""
    global _tiers_cache, _tiers_cache_time

    # Check cache
    if _tiers_cache and _tiers_cache_time:
        if (datetime.now() - _tiers_cache_time).seconds < TIER_CACHE_TTL:
            return _tiers_cache

    try:
        result = supabase.table('tiers').select('*').eq('is_active', True).execute()
        if result.data:
            _tiers_cache = {tier['name']: tier for tier in result.data}
            _tiers_cache_time = datetime.now()
            return _tiers_cache
    except Exception as e:
        app.logger.error(f"Error fetching tiers: {e}")

    # Fallback to defaults if DB unavailable
    return {
        'lifeline': {'id': None, 'name': 'lifeline', 'price_cents': 100, 'max_coverage_cents': 15000, 'services_covered': ['road_ambulance']},
        'shield': {'id': None, 'name': 'shield', 'price_cents': 250, 'max_coverage_cents': 50000, 'services_covered': ['road_ambulance', 'air_ambulance', 'stabilization']},
        'guardian': {'id': None, 'name': 'guardian', 'price_cents': 500, 'max_coverage_cents': 100000, 'services_covered': ['road_ambulance', 'air_ambulance', 'stabilization', 'transfer', 'emergency_fund']},
    }


def get_tier(slug: str) -> dict:
    """Get a specific tier by slug."""
    tiers = get_tiers()
    return tiers.get(slug)


def get_tier_by_id(tier_id: str) -> dict:
    """Get a tier by its UUID."""
    tiers = get_tiers()
    for tier in tiers.values():
        if tier.get('id') == tier_id:
            return tier
    return None

# Private key for Flow decryption
private_key = None


def load_private_key():
    """
    Load RSA private key for WhatsApp Flow decryption.

    Uses WHATSAPP_PRIVATE_KEY env var - raw PEM string with \\n for newlines.
    """
    global private_key
    key_password = os.getenv('WHATSAPP_PRIVATE_KEY_PASSWORD')
    password_bytes = key_password.encode() if key_password else None

    try:
        key_env = os.getenv('WHATSAPP_PRIVATE_KEY')
        if key_env:
            # Replace literal \n with actual newlines
            key_pem = key_env.replace('\\n', '\n').strip()
            private_key = serialization.load_pem_private_key(
                key_pem.encode(),
                password=password_bytes,
                backend=default_backend()
            )
            app.logger.info("Private key loaded successfully")
            return

        app.logger.error("No private key configured. Set WHATSAPP_PRIVATE_KEY env var")

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
# SMS GATEWAY HELPERS (Android SMS Gateway - Cloud Mode)
# =============================================================================

def send_sms(phone_number: str, message: str, ttl: int = 86400) -> dict:
    """
    Send SMS via Android SMS Gateway Cloud API.

    Args:
        phone_number: Recipient phone number (e.g., +263771234567)
        message: SMS message text
        ttl: Time to live in seconds (default 24 hours)

    Returns:
        API response dict with message ID and state
    """
    url = f"{SMS_GATEWAY_CONFIG['base_url']}/3rdparty/v1/message"

    # HTTP Basic Auth
    auth = (SMS_GATEWAY_CONFIG['username'], SMS_GATEWAY_CONFIG['password'])

    payload = {
        'message': message,
        'phoneNumbers': [phone_number],
        'ttl': ttl
    }

    # Add device ID if configured (for multi-device setups)
    if SMS_GATEWAY_CONFIG.get('device_id'):
        payload['id'] = SMS_GATEWAY_CONFIG['device_id']

    try:
        response = requests.post(url, auth=auth, json=payload)
        response.raise_for_status()
        result = response.json()
        app.logger.info(f"SMS sent to {phone_number}: {result}")
        return result
    except requests.exceptions.RequestException as e:
        app.logger.error(f"SMS sending failed to {phone_number}: {e}")
        return {'error': str(e), 'state': 'Failed'}


def send_bulk_sms(phone_numbers: list, message: str, ttl: int = 86400) -> dict:
    """
    Send SMS to multiple recipients via Android SMS Gateway.

    Args:
        phone_numbers: List of recipient phone numbers
        message: SMS message text
        ttl: Time to live in seconds

    Returns:
        API response dict
    """
    url = f"{SMS_GATEWAY_CONFIG['base_url']}/3rdparty/v1/message"
    auth = (SMS_GATEWAY_CONFIG['username'], SMS_GATEWAY_CONFIG['password'])

    payload = {
        'message': message,
        'phoneNumbers': phone_numbers,
        'ttl': ttl
    }

    if SMS_GATEWAY_CONFIG.get('device_id'):
        payload['id'] = SMS_GATEWAY_CONFIG['device_id']

    try:
        response = requests.post(url, auth=auth, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Bulk SMS failed: {e}")
        return {'error': str(e), 'state': 'Failed'}


def get_sms_status(message_id: str) -> dict:
    """
    Get status of a sent SMS message.

    Args:
        message_id: The ID returned when message was sent

    Returns:
        Message status dict
    """
    url = f"{SMS_GATEWAY_CONFIG['base_url']}/3rdparty/v1/message/{message_id}"
    auth = (SMS_GATEWAY_CONFIG['username'], SMS_GATEWAY_CONFIG['password'])

    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"SMS status check failed for {message_id}: {e}")
        return {'error': str(e)}


def notify_via_sms(phone_number: str, member_name: str, incident: dict):
    """
    Send emergency SMS notification (fallback when WhatsApp unavailable).
    """
    message = (
        f"LIFETAP EMERGENCY: {member_name} needs help. "
        f"Incident: {incident.get('incident_number')}. "
        f"Track: lifetap.co.zw/t/{incident.get('incident_number')}"
    )
    return send_sms(phone_number, message)


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


def get_member_subscription(member_uuid: str) -> dict:
    """Get active subscription for a member with tier details."""
    try:
        result = supabase.table('subscriptions').select(
            '*, tiers(*)'
        ).eq('member_id', member_uuid).eq('status', 'active').single().execute()
        return result.data
    except Exception:
        return None


def create_incident(data: dict) -> dict:
    """Create emergency incident in Supabase."""
    try:
        # Generate incident number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        incident_number = f"INC-{timestamp}"

        # Get member UUID from member_id string
        member_id_str = data.get('member_id')
        member = None
        member_uuid = None
        member_tier = None

        if member_id_str:
            member = get_member_by_id(member_id_str)
            if member:
                member_uuid = member.get('id')
                # Get subscription tier
                subscription = get_member_subscription(member_uuid)
                if subscription and subscription.get('tiers'):
                    member_tier = subscription['tiers'].get('name')

        incident_data = {
            'incident_number': incident_number,
            'member_id': member_uuid,
            'member_tier': member_tier,
            'emergency_type': data.get('emergency_type'),
            'patient_conscious': data.get('conscious') == 'yes' if data.get('conscious') else None,
            'patient_breathing': data.get('breathing') == 'yes' if data.get('breathing') else None,
            'victim_count': int(data.get('victim_count', 1)) if data.get('victim_count') else 1,
            'scene_description': data.get('scene_description'),
            'activated_by_phone': data.get('bystander_phone'),
            'activation_method': 'whatsapp',
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
# PAYMENT HELPERS
# =============================================================================

def generate_transaction_ref() -> str:
    """Generate unique transaction reference."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = uuid.uuid4().hex[:6].upper()
    return f"LT-{timestamp}-{random_part}"


def create_subscription_payment(member_id: str, tier_slug: str, phone_number: str) -> dict:
    """
    Initiate subscription payment via Paynow.

    Returns dict with payment URL or error.
    """
    if not paynow:
        return {'error': 'Payment system not configured'}

    tier = get_tier(tier_slug)
    if not tier:
        return {'error': f'Invalid tier: {tier_slug}'}

    price_cents = tier.get('price_cents')

    price_usd = price_cents / 100
    transaction_ref = generate_transaction_ref()

    try:
        # Create Paynow payment
        payment = paynow.create_payment(transaction_ref, f"member-{member_id}@lifetap.co.zw")
        payment.add('LifeTap Subscription', price_usd)

        # Send to mobile money
        response = paynow.send_mobile(payment, phone_number, 'ecocash')

        if response.success:
            # Store transaction in database
            transaction_data = {
                'transaction_ref': transaction_ref,
                'external_ref': response.poll_url,
                'member_id': member_id,
                'amount_cents': price_cents,
                'currency': 'USD',
                'transaction_type': 'subscription_payment',
                'status': 'awaiting_delivery',
                'payment_method': 'ecocash',
                'phone_number': phone_number,
                'paynow_poll_url': response.poll_url,
                'description': f"LifeTap {tier.get('name', tier_slug.title())} Subscription",
                'initiated_at': datetime.now().isoformat()
            }

            result = supabase.table('transactions').insert(transaction_data).execute()

            return {
                'success': True,
                'transaction_ref': transaction_ref,
                'poll_url': response.poll_url,
                'instructions': response.instructions if hasattr(response, 'instructions') else None
            }
        else:
            return {'error': response.error or 'Payment initiation failed'}

    except Exception as e:
        app.logger.error(f"Payment error: {e}")
        return {'error': str(e)}


def check_payment_status(poll_url: str) -> dict:
    """Check payment status from Paynow."""
    if not paynow:
        return {'error': 'Payment system not configured'}

    try:
        status = paynow.check_transaction_status(poll_url)
        return {
            'paid': status.paid,
            'status': status.status,
            'amount': status.amount if hasattr(status, 'amount') else None,
            'reference': status.reference if hasattr(status, 'reference') else None
        }
    except Exception as e:
        app.logger.error(f"Status check error: {e}")
        return {'error': str(e)}


def activate_subscription(member_id: str, tier_slug: str, transaction_id: str = None) -> dict:
    """Activate or renew a member's subscription."""
    try:
        tier = get_tier(tier_slug)
        if not tier or not tier.get('id'):
            app.logger.error(f"Tier not found: {tier_slug}")
            return None

        now = datetime.now()
        expires_at = now + timedelta(days=30)

        subscription_data = {
            'member_id': member_id,
            'tier_id': tier['id'],
            'status': 'active',
            'started_at': now.isoformat(),
            'expires_at': expires_at.isoformat(),
            'auto_renew': True
        }

        # Check for existing subscription
        existing = supabase.table('subscriptions').select('id').eq(
            'member_id', member_id
        ).execute()

        if existing.data:
            # Update existing
            result = supabase.table('subscriptions').update(subscription_data).eq(
                'member_id', member_id
            ).execute()
        else:
            # Create new
            result = supabase.table('subscriptions').insert(subscription_data).execute()

        # Update member status to active
        supabase.table('members').update({'status': 'active'}).eq('id', member_id).execute()

        # Link transaction to subscription if provided
        if transaction_id and result.data:
            supabase.table('transactions').update({
                'subscription_id': result.data[0]['id'],
                'status': 'paid',
                'paid_at': now.isoformat()
            }).eq('id', transaction_id).execute()

        return result.data[0] if result.data else None

    except Exception as e:
        app.logger.error(f"Subscription activation error: {e}")
        return None


def generate_payment_token(incident_id: str, member_id: str, subscription_id: str, tier_id: str) -> dict:
    """Generate a Guaranteed Payment Token for an emergency."""
    try:
        tier = get_tier_by_id(tier_id)
        if not tier:
            # Fallback to lifeline
            tier = get_tier('lifeline')

        # Generate token code
        token_code = f"GPT-{uuid.uuid4().hex[:8].upper()}"

        token_data = {
            'token_code': token_code,
            'incident_id': incident_id,
            'member_id': member_id,
            'subscription_id': subscription_id,
            'tier_id': tier_id,
            'max_coverage_cents': tier.get('max_coverage_cents', 15000),
            'services_covered': tier.get('services_included', ['road_ambulance']),
            'status': 'active',
            'issued_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }

        result = supabase.table('payment_tokens').insert(token_data).execute()

        if result.data:
            # Link token to incident
            supabase.table('incidents').update({
                'payment_token_id': result.data[0]['id']
            }).eq('id', incident_id).execute()

            return result.data[0]

        return None

    except Exception as e:
        app.logger.error(f"Token generation error: {e}")
        return None


def verify_payment_token(token_code: str) -> dict:
    """Verify a payment token for ambulance providers."""
    try:
        result = supabase.table('payment_tokens').select(
            '*, members(*), incidents(*), tiers(*)'
        ).eq('token_code', token_code).single().execute()

        if not result.data:
            return {'valid': False, 'error': 'Token not found'}

        token = result.data
        tier = token.get('tiers', {})

        # Check status
        if token['status'] != 'active':
            return {'valid': False, 'error': f"Token status: {token['status']}"}

        # Check expiry
        expires_at = datetime.fromisoformat(token['expires_at'].replace('Z', '+00:00'))
        if datetime.now(expires_at.tzinfo) > expires_at:
            return {'valid': False, 'error': 'Token expired'}

        return {
            'valid': True,
            'token_code': token_code,
            'tier': tier.get('name') if tier else None,
            'tier_display_name': tier.get('display_name') if tier else None,
            'max_coverage_cents': token['max_coverage_cents'],
            'services_covered': token['services_covered'],
            'member': token.get('members'),
            'incident': token.get('incidents')
        }

    except Exception as e:
        app.logger.error(f"Token verification error: {e}")
        return {'valid': False, 'error': str(e)}


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

        # Encrypt and return as plain text (not JSON)
        encrypted = encrypt_flow_response(response)
        return encrypted, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        app.logger.error(f"Flow error: {e}")
        return str(e), 500, {'Content-Type': 'text/plain'}


# =============================================================================
# WHATSAPP WEBHOOK (for regular messages)
# =============================================================================

# Import chatbot handler
from chatbot.handlers import MessageHandler
import asyncio

# Initialize chatbot handler
message_handler = MessageHandler(supabase)


def run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


@app.route('/whatsapp/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == WHATSAPP_CONFIG['webhook_verify_token']:
        return challenge, 200

    return 'Forbidden', 403


def _process_webhook_message(message: dict):
    """Process a single webhook message using async MessageHandler."""
    msg_id = message.get('id')
    msg_type = message.get('type')
    from_number = message.get('from')

    app.logger.info(f"Processing {msg_type} from {from_number} (id: {msg_id})")

    try:
        # Extract message data based on type
        if msg_type == 'text':
            message_data = message.get('text', {})

        elif msg_type == 'interactive':
            message_data = message.get('interactive', {})

        elif msg_type == 'location':
            message_data = message.get('location', {})

        elif msg_type == 'button':
            # Template button response - convert to text
            button_data = message.get('button', {})
            message_data = {'body': button_data.get('text', '')}
            msg_type = 'text'

        elif msg_type in ('image', 'audio', 'video', 'document', 'sticker'):
            # Media messages - send help text
            app.logger.info(f"Media message received: {msg_type}")
            from chatbot import messages as chat_messages
            chat_messages.send_text(
                from_number,
                "*LifeTap Emergency Response*\n\nTo activate emergency services, tap the NFC card or scan QR code on a member's LifeTap card."
            )
            return

        else:
            app.logger.info(f"Ignoring message type: {msg_type}")
            return

        # Process message via async handler
        result = run_async(
            message_handler.process_message(
                user_id=from_number,
                message_type=msg_type,
                message_data=message_data,
                message_id=msg_id
            )
        )
        app.logger.info(f"Message processed: {result.get('status', 'unknown')}")

    except Exception as e:
        app.logger.error(f"Error processing message {msg_id}: {e}")
        import traceback
        app.logger.error(traceback.format_exc())


@app.route('/whatsapp/webhook', methods=['POST'])
def receive_webhook():
    """
    Receive WhatsApp messages and events.

    WhatsApp expects 200 OK within 20 seconds or it will retry.
    We return immediately and process messages.
    """
    data = request.get_json()

    # Log webhook receipt (compact)
    app.logger.info(f"Webhook received from WhatsApp")

    try:
        # Validate webhook structure
        if not data or 'entry' not in data:
            app.logger.warning("Invalid webhook payload - missing entry")
            return jsonify({'status': 'ok'}), 200

        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})

                # Skip status updates (delivered, read, etc.)
                if 'statuses' in value:
                    app.logger.debug("Ignoring status update")
                    continue

                # Process messages
                messages_list = value.get('messages', [])
                for message in messages_list:
                    _process_webhook_message(message)

    except Exception as e:
        app.logger.error(f"Webhook error: {e}")
        import traceback
        app.logger.error(traceback.format_exc())

    # Always return 200 to prevent WhatsApp retries
    return jsonify({'status': 'ok'}), 200


# =============================================================================
# PAYMENT ENDPOINTS
# =============================================================================

@app.route('/api/payments/initiate', methods=['POST'])
def initiate_payment():
    """Initiate a subscription payment."""
    data = request.get_json()

    member_id = data.get('member_id')
    tier = data.get('tier', 'lifeline')
    phone_number = data.get('phone_number')

    if not member_id or not phone_number:
        return jsonify({'error': 'member_id and phone_number required'}), 400

    result = create_subscription_payment(member_id, tier, phone_number)

    if result.get('error'):
        return jsonify(result), 400

    return jsonify(result)


@app.route('/api/payments/status/<transaction_ref>', methods=['GET'])
def payment_status(transaction_ref):
    """Check payment status."""
    try:
        # Get transaction from database
        result = supabase.table('transactions').select('*').eq(
            'transaction_ref', transaction_ref
        ).single().execute()

        if not result.data:
            return jsonify({'error': 'Transaction not found'}), 404

        transaction = result.data

        # Check status with Paynow if pending
        if transaction['status'] == 'awaiting_delivery' and transaction.get('paynow_poll_url'):
            paynow_status = check_payment_status(transaction['paynow_poll_url'])

            if paynow_status.get('paid'):
                # Activate subscription
                activate_subscription(
                    transaction['member_id'],
                    'lifeline',  # Default tier, should be stored in transaction
                    transaction['id']
                )
                transaction['status'] = 'paid'

        return jsonify(transaction)

    except Exception as e:
        app.logger.error(f"Status check error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/payments/callback', methods=['POST'])
def payment_callback():
    """Paynow payment callback/result URL."""
    data = request.form.to_dict() or request.get_json() or {}

    app.logger.info(f"Payment callback: {data}")

    reference = data.get('reference')
    status = data.get('status')
    paynow_reference = data.get('paynowreference')

    if not reference:
        return jsonify({'error': 'No reference provided'}), 400

    try:
        # Find transaction
        result = supabase.table('transactions').select('*').eq(
            'transaction_ref', reference
        ).single().execute()

        if not result.data:
            return jsonify({'error': 'Transaction not found'}), 404

        transaction = result.data

        # Update transaction
        update_data = {
            'paynow_status': status,
            'paynow_reference': paynow_reference
        }

        if status and status.lower() == 'paid':
            update_data['status'] = 'paid'
            update_data['paid_at'] = datetime.now().isoformat()

            # Activate subscription
            # Get tier from metadata or default
            tier = transaction.get('metadata', {}).get('tier', 'lifeline')
            activate_subscription(transaction['member_id'], tier, transaction['id'])

        elif status and status.lower() in ['failed', 'cancelled']:
            update_data['status'] = 'failed'
            update_data['failed_at'] = datetime.now().isoformat()

        supabase.table('transactions').update(update_data).eq(
            'id', transaction['id']
        ).execute()

        return jsonify({'status': 'ok'})

    except Exception as e:
        app.logger.error(f"Callback error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tokens/verify/<token_code>', methods=['GET'])
def verify_token(token_code):
    """Verify a payment token (for ambulance providers)."""
    result = verify_payment_token(token_code)

    if not result.get('valid'):
        return jsonify(result), 404 if result.get('error') == 'Token not found' else 400

    return jsonify(result)


@app.route('/api/members', methods=['POST'])
def create_member():
    """Register a new member."""
    data = request.get_json()

    required = ['first_name', 'last_name', 'phone_number']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    try:
        member_data = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone_number': data['phone_number'],
            'email': data.get('email'),
            'date_of_birth': data.get('date_of_birth'),
            'gender': data.get('gender'),
            'address_line1': data.get('address_line1'),
            'address_city': data.get('address_city'),
            'address_province': data.get('address_province'),
            'registration_channel': data.get('registration_channel', 'whatsapp'),
            'status': 'pending'
        }

        result = supabase.table('members').insert(member_data).execute()

        if result.data:
            member = result.data[0]

            # Create empty EMR record
            supabase.table('emr_records').insert({
                'member_id': member['id']
            }).execute()

            # Add next of kin if provided
            if data.get('next_of_kin'):
                nok = data['next_of_kin']
                supabase.table('next_of_kin').insert({
                    'member_id': member['id'],
                    'full_name': nok.get('full_name'),
                    'relationship': nok.get('relationship'),
                    'phone_number': nok.get('phone_number'),
                    'is_primary': True
                }).execute()

            return jsonify(member), 201

        return jsonify({'error': 'Failed to create member'}), 500

    except Exception as e:
        app.logger.error(f"Member creation error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/members/<member_id>', methods=['GET'])
def get_member(member_id):
    """Get member by member_id (LT-XXXX format)."""
    member = get_member_by_id(member_id)

    if not member:
        return jsonify({'error': 'Member not found'}), 404

    return jsonify(member)


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
