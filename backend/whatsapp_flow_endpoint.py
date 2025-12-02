"""
LifeTap WhatsApp Flow Endpoint
Handles encrypted requests from WhatsApp Flows and returns encrypted responses.

Based on WhatsApp Flow Endpoint specification:
https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint

Encryption: AES-128-GCM with RSA-OAEP key exchange
"""

import os
import json
import base64
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify, g
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from functools import wraps

app = Flask(__name__)

# Configuration - Load from environment variables
PRIVATE_KEY_PATH = os.getenv('WHATSAPP_PRIVATE_KEY_PATH', 'keys/private.pem')
PRIVATE_KEY_PASSWORD = os.getenv('WHATSAPP_PRIVATE_KEY_PASSWORD', None)
FLOW_TOKEN_SECRET = os.getenv('WHATSAPP_FLOW_TOKEN_SECRET', 'your-flow-token-secret')

# Load private key on startup
def load_private_key():
    """Load the RSA private key for decrypting AES keys from WhatsApp."""
    try:
        with open(PRIVATE_KEY_PATH, 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=PRIVATE_KEY_PASSWORD.encode() if PRIVATE_KEY_PASSWORD else None,
                backend=default_backend()
            )
        return private_key
    except FileNotFoundError:
        app.logger.error(f"Private key not found at {PRIVATE_KEY_PATH}")
        return None
    except Exception as e:
        app.logger.error(f"Error loading private key: {e}")
        return None

private_key = None


def decrypt_request(encrypted_flow_data: str, encrypted_aes_key: str, initial_vector: str) -> dict:
    """
    Decrypt incoming WhatsApp Flow request.

    WhatsApp sends:
    1. encrypted_aes_key: AES key encrypted with your public RSA key
    2. initial_vector: IV for AES-GCM
    3. encrypted_flow_data: The actual payload encrypted with AES-GCM

    Steps:
    1. Decrypt the AES key using RSA-OAEP with SHA-256
    2. Use AES-128-GCM to decrypt the payload
    """
    global private_key

    if private_key is None:
        private_key = load_private_key()
        if private_key is None:
            raise Exception("Private key not loaded")

    # Decode base64 inputs
    encrypted_aes_key_bytes = base64.b64decode(encrypted_aes_key)
    iv_bytes = base64.b64decode(initial_vector)
    encrypted_flow_data_bytes = base64.b64decode(encrypted_flow_data)

    # Step 1: Decrypt AES key using RSA-OAEP
    aes_key = private_key.decrypt(
        encrypted_aes_key_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Step 2: Decrypt payload using AES-128-GCM
    # Note: The tag is appended to the ciphertext in AES-GCM
    aesgcm = AESGCM(aes_key)
    decrypted_data = aesgcm.decrypt(iv_bytes, encrypted_flow_data_bytes, None)

    # Parse JSON payload
    flow_data = json.loads(decrypted_data.decode('utf-8'))

    # Store AES key and IV for response encryption
    g.aes_key = aes_key
    g.iv = iv_bytes

    return flow_data


def encrypt_response(response_data: dict) -> str:
    """
    Encrypt response back to WhatsApp using the same AES key.

    Uses AES-128-GCM with a flipped IV (for uniqueness).
    """
    aes_key = g.aes_key
    iv = g.iv

    # Flip the IV for response (WhatsApp requirement)
    flipped_iv = bytes(~b & 0xFF for b in iv)

    # Encrypt response
    aesgcm = AESGCM(aes_key)
    response_json = json.dumps(response_data).encode('utf-8')
    encrypted_response = aesgcm.encrypt(flipped_iv, response_json, None)

    # Return base64 encoded
    return base64.b64encode(encrypted_response).decode('utf-8')


def validate_flow_token(flow_token: str) -> bool:
    """Validate the flow token to ensure request authenticity."""
    # Implement your flow token validation logic
    # This could be a signature check or database lookup
    return True  # For now, accept all tokens


# ============================================================================
# FLOW ENDPOINT
# ============================================================================

@app.route('/whatsapp/flow', methods=['POST'])
def handle_flow_request():
    """
    Main WhatsApp Flow endpoint.

    Receives encrypted requests, processes them, and returns encrypted responses.
    """
    try:
        # Get encrypted request data
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        encrypted_flow_data = data.get('encrypted_flow_data')
        encrypted_aes_key = data.get('encrypted_aes_key')
        initial_vector = data.get('initial_vector')

        if not all([encrypted_flow_data, encrypted_aes_key, initial_vector]):
            return jsonify({"error": "Missing encryption parameters"}), 400

        # Decrypt the request
        flow_data = decrypt_request(encrypted_flow_data, encrypted_aes_key, initial_vector)

        app.logger.info(f"Decrypted flow data: {json.dumps(flow_data, indent=2)}")

        # Extract flow information
        action = flow_data.get('action')
        screen = flow_data.get('screen')
        data_payload = flow_data.get('data', {})
        flow_token = flow_data.get('flow_token')
        version = flow_data.get('version')

        # Validate flow token
        if not validate_flow_token(flow_token):
            error_response = {
                "version": version,
                "screen": "ERROR",
                "data": {
                    "error_message": "Invalid flow token"
                }
            }
            return jsonify({"encrypted_response": encrypt_response(error_response)})

        # Route to appropriate handler based on action
        if action == 'ping':
            # Health check
            response = handle_ping(flow_data)
        elif action == 'INIT':
            # Initial screen request
            response = handle_init(flow_data)
        elif action == 'data_exchange':
            # User submitted data
            response = handle_data_exchange(screen, data_payload, flow_data)
        elif action == 'BACK':
            # User pressed back
            response = handle_back(screen, flow_data)
        else:
            response = {
                "version": version,
                "screen": "ERROR",
                "data": {
                    "error_message": f"Unknown action: {action}"
                }
            }

        # Encrypt and return response
        encrypted_response = encrypt_response(response)

        return jsonify({"encrypted_response": encrypted_response})

    except Exception as e:
        app.logger.error(f"Error handling flow request: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# FLOW HANDLERS
# ============================================================================

def handle_ping(flow_data: dict) -> dict:
    """Handle health check ping from WhatsApp."""
    return {
        "version": flow_data.get('version'),
        "data": {
            "status": "active"
        }
    }


def handle_init(flow_data: dict) -> dict:
    """
    Handle initial flow request.

    This is called when the flow is first opened.
    For emergency flow, we need to fetch member data and populate the screen.
    """
    version = flow_data.get('version')
    flow_token = flow_data.get('flow_token')

    # The flow_token contains the member_id from the NFC/QR scan
    # Format: EMERGENCY:LT-2025-A7X9K3
    member_id = extract_member_id(flow_token)

    if not member_id:
        return {
            "version": version,
            "screen": "EMERGENCY_SCREEN",
            "data": {
                "member_name": "Unknown",
                "member_id": "N/A",
                "blood_type": "Unknown",
                "allergies": "Unknown",
                "conditions": "Unknown"
            }
        }

    # Fetch member data from database
    member_data = get_member_data(member_id)

    return {
        "version": version,
        "screen": "EMERGENCY_SCREEN",
        "data": {
            "member_name": member_data.get('name', 'Unknown'),
            "member_id": member_id,
            "blood_type": member_data.get('blood_type', 'Unknown'),
            "allergies": member_data.get('allergies', 'None known'),
            "conditions": member_data.get('conditions', 'None known')
        }
    }


def handle_data_exchange(screen: str, data: dict, flow_data: dict) -> dict:
    """
    Handle user data submission from a flow screen.

    For emergency flow, this receives the situation assessment.
    """
    version = flow_data.get('version')

    if screen == 'EMERGENCY_SCREEN':
        return handle_emergency_submission(data, flow_data)

    # Default response
    return {
        "version": version,
        "screen": screen,
        "data": {}
    }


def handle_emergency_submission(data: dict, flow_data: dict) -> dict:
    """
    Process emergency form submission.

    Data received:
    - member_id: The LifeTap member ID
    - emergency_type: Type of emergency (road_accident, collapse, etc.)
    - conscious: Is patient conscious (yes/no/unsure)
    - breathing: Is patient breathing (yes/struggling/no/unsure)
    - victim_count: Number of victims (1/2/3/4+)
    - scene_description: Optional description
    """
    version = flow_data.get('version')

    member_id = data.get('member_id')
    emergency_type = data.get('emergency_type')
    conscious = data.get('conscious')
    breathing = data.get('breathing')
    victim_count = data.get('victim_count')
    scene_description = data.get('scene_description', '')

    app.logger.info(f"""
    ========== EMERGENCY ACTIVATED ==========
    Member ID: {member_id}
    Emergency Type: {emergency_type}
    Conscious: {conscious}
    Breathing: {breathing}
    Victim Count: {victim_count}
    Scene Description: {scene_description}
    =========================================
    """)

    # Create incident in database
    incident_id = create_emergency_incident(
        member_id=member_id,
        emergency_type=emergency_type,
        conscious=conscious,
        breathing=breathing,
        victim_count=victim_count,
        scene_description=scene_description
    )

    # Trigger async processes:
    # 1. Send location request message via WhatsApp
    # 2. Notify Next of Kin
    # 3. Alert ambulance providers
    trigger_emergency_workflow(incident_id, member_id)

    # Close the flow with success
    # WhatsApp will then prompt for location via separate message
    return {
        "version": version,
        "screen": "SUCCESS",
        "data": {
            "extension_message_response": {
                "params": {
                    "flow_token": flow_data.get('flow_token'),
                    "incident_id": incident_id
                }
            }
        }
    }


def handle_back(screen: str, flow_data: dict) -> dict:
    """Handle back button press."""
    version = flow_data.get('version')

    # For single-screen emergency flow, just return same screen
    return {
        "version": version,
        "screen": "EMERGENCY_SCREEN",
        "data": {}
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_member_id(flow_token: str) -> str:
    """Extract member ID from flow token."""
    if not flow_token:
        return None

    # Expected format: EMERGENCY:LT-2025-A7X9K3
    if ':' in flow_token:
        parts = flow_token.split(':')
        if len(parts) >= 2:
            return parts[1]

    # Or could be just the member ID
    if flow_token.startswith('LT-'):
        return flow_token

    return None


def get_member_data(member_id: str) -> dict:
    """
    Fetch member data from Supabase.

    TODO: Replace with actual Supabase query
    """
    # Mock data for testing
    mock_members = {
        'LT-2025-A7X9K3': {
            'name': 'John Moyo',
            'blood_type': 'O+',
            'allergies': 'Penicillin',
            'conditions': 'Diabetic'
        },
        'LT-2025-B8Y2M5': {
            'name': 'Mary Ncube',
            'blood_type': 'A-',
            'allergies': 'None',
            'conditions': 'Asthma'
        }
    }

    return mock_members.get(member_id, {
        'name': 'Unknown Member',
        'blood_type': 'Unknown',
        'allergies': 'Unknown',
        'conditions': 'Unknown'
    })


def create_emergency_incident(
    member_id: str,
    emergency_type: str,
    conscious: str,
    breathing: str,
    victim_count: str,
    scene_description: str
) -> str:
    """
    Create emergency incident in Supabase.

    TODO: Replace with actual Supabase insert
    """
    # Generate incident ID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    incident_id = f"INC-{timestamp}"

    app.logger.info(f"Created incident: {incident_id}")

    # TODO: Insert into Supabase
    # supabase.table('incidents').insert({
    #     'incident_number': incident_id,
    #     'member_id': member_id,
    #     'emergency_type': emergency_type,
    #     'patient_conscious': conscious,
    #     'patient_breathing': breathing,
    #     'victim_count': victim_count,
    #     'scene_description': scene_description,
    #     'status': 'activated',
    #     'activated_at': datetime.now().isoformat()
    # }).execute()

    return incident_id


def trigger_emergency_workflow(incident_id: str, member_id: str):
    """
    Trigger the emergency workflow.

    This runs async processes:
    1. Send WhatsApp message asking for location
    2. Notify Next of Kin
    3. Prepare ambulance dispatch
    """
    app.logger.info(f"Triggering emergency workflow for {incident_id}")

    # TODO: Implement these as background tasks
    # - send_location_request(incident_id, bystander_phone)
    # - notify_next_of_kin(member_id, incident_id)
    # - prepare_ambulance_dispatch(incident_id)

    pass


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/whatsapp/flow/health', methods=['GET'])
def health_check():
    """Health check endpoint for WhatsApp to verify your server is running."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "lifetap-whatsapp-flow"
    })


# ============================================================================
# SIGNATURE VERIFICATION (Optional but recommended)
# ============================================================================

def verify_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    """
    Verify WhatsApp signature for additional security.

    WhatsApp signs requests with your app secret.
    """
    expected_signature = hashlib.sha256(
        payload + app_secret.encode()
    ).hexdigest()

    return signature == expected_signature


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
