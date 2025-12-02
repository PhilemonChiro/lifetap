# LifeTap WhatsApp Flow Backend

Flask-based backend service for handling WhatsApp Flows encryption/decryption and emergency response logic.

## Features

- WhatsApp Flow endpoint with AES-GCM encryption
- WhatsApp webhook for receiving messages and locations
- Supabase integration for data storage
- Paynow payment integration
- SMS Gateway support

## Setup

### 1. Generate RSA Keys

WhatsApp Flows require RSA key pairs for encryption:

```bash
# Create keys directory
mkdir -p keys

# Generate private key (no password for simplicity, or add -des3 for password protection)
openssl genrsa -out keys/private.pem 2048

# Extract public key
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# View public key (you'll upload this to WhatsApp)
cat keys/public.pem
```

### 2. Upload Public Key to WhatsApp

Use the Graph API to upload your public key:

```bash
curl -X POST \
  "https://graph.facebook.com/v18.0/{WHATSAPP_BUSINESS_ACCOUNT_ID}/whatsapp_business_encryption" \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "business_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
  }'
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
flask run --debug

# Or with Docker
docker-compose -f docker-compose.dev.yml up
```

### 5. Production Deployment (Coolify)

1. Push code to your Git repository
2. In Coolify, create a new service from Docker Compose
3. Select `docker-compose.coolify.yml`
4. Add environment variables in Coolify dashboard
5. For the private key, either:
   - Base64 encode it: `base64 -w 0 keys/private.pem` and set as `WHATSAPP_PRIVATE_KEY`
   - Or mount as a volume

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/whatsapp/flow` | POST | WhatsApp Flow encrypted requests |
| `/whatsapp/webhook` | GET | Webhook verification |
| `/whatsapp/webhook` | POST | Receive WhatsApp messages |

## WhatsApp Flow Encryption

The service handles WhatsApp's encryption protocol:

1. **Incoming requests**: Encrypted with AES-128-GCM, key encrypted with your RSA public key
2. **Decryption**: RSA-OAEP to decrypt AES key, then AES-GCM to decrypt payload
3. **Response**: Encrypted with same AES key but flipped IV

## Project Structure

```
backend/
├── app.py                      # Main Flask application
├── whatsapp_flow_endpoint.py   # Standalone flow handler (reference)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production Docker image
├── Dockerfile.dev              # Development Docker image
├── .env.example                # Environment variables template
└── keys/                       # RSA keys (gitignored)
    ├── private.pem
    └── public.pem
```

## Testing the Flow

1. Configure your WhatsApp Flow with the JSON from `whatsapp-flows/emergency-flow.json`
2. Set the Flow endpoint to your server URL
3. Trigger the flow via NFC card scan or test message

## Troubleshooting

### "Private key not loaded"
- Check `WHATSAPP_PRIVATE_KEY` env var or `keys/private.pem` file exists
- Verify key format is valid PEM

### "Decryption failed"
- Ensure the public key uploaded to WhatsApp matches your private key
- Check key password if using encrypted private key

### "Webhook verification failed"
- Verify `WHATSAPP_WEBHOOK_VERIFY_TOKEN` matches what you set in Meta dashboard
