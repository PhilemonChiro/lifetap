# LifeTap Technical Stack

## Confirmed Technology Choices

### Backend & Database
| Component | Technology | Notes |
|-----------|------------|-------|
| **Database** | Supabase (PostgreSQL) | Auth, Realtime, Storage, Edge Functions |
| **Authentication** | Supabase Auth | Phone OTP, JWT tokens |
| **Realtime** | Supabase Realtime | Live incident tracking |
| **Storage** | Supabase Storage | EMR documents, images |
| **Edge Functions** | Supabase Edge Functions (Deno) | API endpoints, webhooks |
| **Row Level Security** | Supabase RLS | Tiered EMR access control |

### Communication
| Component | Technology | Notes |
|-----------|------------|-------|
| **WhatsApp** | Meta WhatsApp Graph API | Direct integration, no middleware |
| **SMS Gateway** | Android SMS Gateway | Self-hosted via https://github.com/capcom6/android-sms-gateway |

### Payments
| Component | Technology | Notes |
|-----------|------------|-------|
| **Payment Gateway** | Paynow Zimbabwe | EcoCash, OneMoney, bank cards |

### Physical Interface
| Component | Technology | Notes |
|-----------|------------|-------|
| **NFC** | Mobile phone NFC | NDEF tags with WhatsApp deep links |
| **QR Code** | Standard QR | Fallback for non-NFC phones |

### Geolocation
| Component | Technology | Notes |
|-----------|------------|-------|
| **Maps & Geocoding** | Google Maps API | Distance matrix, reverse geocoding |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LIFETAP ARCHITECTURE                                │
│                        (Supabase-Centric)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │     CLIENTS      │
                              └────────┬─────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   NFC/QR Card   │          │    WhatsApp     │          │  Admin Portal   │
│   (Physical)    │          │  (Graph API)    │          │   (Web App)     │
└────────┬────────┘          └────────┬────────┘          └────────┬────────┘
         │                            │                            │
         │   Opens WhatsApp           │                            │
         │   with deep link           │                            │
         └────────────────────────────┤                            │
                                      │                            │
                                      ▼                            │
                    ┌─────────────────────────────────┐            │
                    │      SUPABASE EDGE FUNCTIONS    │◄───────────┘
                    │                                 │
                    │  ┌───────────────────────────┐  │
                    │  │ /whatsapp-webhook         │  │ ◄── WhatsApp messages
                    │  │ /emergency-activate       │  │
                    │  │ /verify-token             │  │ ◄── Provider verification
                    │  │ /paynow-callback          │  │ ◄── Payment notifications
                    │  │ /sms-webhook              │  │ ◄── SMS Gateway callbacks
                    │  └───────────────────────────┘  │
                    └───────────────┬─────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────┐
                    │         SUPABASE CORE           │
                    │                                 │
                    │  ┌──────────┐  ┌─────────────┐  │
                    │  │PostgreSQL│  │  Realtime   │  │
                    │  │ + RLS    │  │ Subscriptions│  │
                    │  └──────────┘  └─────────────┘  │
                    │                                 │
                    │  ┌──────────┐  ┌─────────────┐  │
                    │  │  Auth    │  │   Storage   │  │
                    │  │(Phone OTP)│  │ (Documents) │  │
                    │  └──────────┘  └─────────────┘  │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │  EXTERNAL SERVICES  │       │    SELF-HOSTED      │
        │                     │       │                     │
        │  • WhatsApp Graph   │       │  • Android SMS      │
        │  • Paynow           │       │    Gateway          │
        │  • Google Maps      │       │                     │
        └─────────────────────┘       └─────────────────────┘
```

---

## Supabase Database Schema

### Tables Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE TABLES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

CORE TABLES:
├── members              (Member profiles)
├── subscriptions        (Subscription records)
├── cards                (NFC/QR card tracking)
├── next_of_kin          (Emergency contacts)
├── emr_records          (Medical records)
├── emr_documents        (Stored in Supabase Storage)
├── emr_access_logs      (Audit trail)

EMERGENCY TABLES:
├── incidents            (Emergency activations)
├── payment_tokens       (Guaranteed Payment Tokens)
├── incident_status_history

PAYMENT TABLES:
├── payment_methods      (Member payment methods)
├── transactions         (Paynow transactions)
├── disbursements        (Provider payments)

PROVIDER TABLES:
├── ambulance_providers  (Registered providers)
├── claims               (Provider claims)

NOTIFICATION TABLES:
├── notification_templates
├── notifications        (Sent messages log)

ADMIN TABLES:
├── admin_users
├── audit_logs
```

---

## Edge Functions Structure

```
supabase/functions/
├── whatsapp-webhook/        # Receives WhatsApp messages
│   └── index.ts
├── whatsapp-send/           # Sends WhatsApp messages
│   └── index.ts
├── emergency-activate/      # Triggers emergency response
│   └── index.ts
├── verify-token/            # Provider token verification
│   └── index.ts
├── paynow-initiate/         # Start payment
│   └── index.ts
├── paynow-callback/         # Payment confirmation
│   └── index.ts
├── sms-send/                # Send SMS via Android Gateway
│   └── index.ts
├── sms-webhook/             # Receive SMS status
│   └── index.ts
├── member-register/         # New member registration
│   └── index.ts
├── subscription-renew/      # Subscription renewal
│   └── index.ts
├── emr-summary/             # Get EMR for emergency
│   └── index.ts
├── incident-track/          # Real-time incident tracking
│   └── index.ts
├── claim-submit/            # Provider claim submission
│   └── index.ts
└── admin-stats/             # Dashboard statistics
    └── index.ts
```

---

## Integration Details

### 1. WhatsApp Graph API Integration

```typescript
// Configuration
const WHATSAPP_CONFIG = {
  apiVersion: 'v18.0',
  phoneNumberId: process.env.WHATSAPP_PHONE_NUMBER_ID,
  businessAccountId: process.env.WHATSAPP_BUSINESS_ACCOUNT_ID,
  accessToken: process.env.WHATSAPP_ACCESS_TOKEN,
  webhookVerifyToken: process.env.WHATSAPP_WEBHOOK_VERIFY_TOKEN,
};

// Webhook endpoint: POST /functions/v1/whatsapp-webhook
// Send message endpoint: POST /functions/v1/whatsapp-send

// Message types to handle:
// - text (emergency trigger, commands)
// - location (GPS coordinates)
// - interactive (button responses)
```

### 2. Paynow Integration

```typescript
// Configuration
const PAYNOW_CONFIG = {
  integrationId: process.env.PAYNOW_INTEGRATION_ID,
  integrationKey: process.env.PAYNOW_INTEGRATION_KEY,
  resultUrl: 'https://<project>.supabase.co/functions/v1/paynow-callback',
  returnUrl: 'https://lifetap.co.zw/payment/complete',
};

// Supported methods:
// - EcoCash (mobile: 077xxxxxxx)
// - OneMoney (mobile: 071xxxxxxx)
// - Bank cards (Visa/Mastercard)

// Flow:
// 1. POST /functions/v1/paynow-initiate
// 2. User completes payment on Paynow
// 3. Paynow calls /functions/v1/paynow-callback
// 4. Update subscription status
```

### 3. Android SMS Gateway Integration

```typescript
// Configuration
const SMS_GATEWAY_CONFIG = {
  baseUrl: process.env.SMS_GATEWAY_URL, // Your hosted instance
  apiKey: process.env.SMS_GATEWAY_API_KEY,
};

// API Endpoints:
// POST /message - Send SMS
// GET /message/{id} - Check status

// Use cases:
// - NOK alerts (fallback when no WhatsApp)
// - OTP verification
// - Subscription reminders
```

### 4. Google Maps API Integration

```typescript
// Configuration
const GOOGLE_MAPS_CONFIG = {
  apiKey: process.env.GOOGLE_MAPS_API_KEY,
};

// APIs to use:
// - Geocoding API (address → coordinates)
// - Reverse Geocoding (coordinates → address)
// - Distance Matrix API (ETA calculation)
// - Static Maps API (map images for WhatsApp)
```

### 5. NFC Card Configuration

```
NFC NDEF Record Structure:
┌─────────────────────────────────────────────────────────────────┐
│ Type: URI                                                       │
│ URI:  https://wa.me/263XXXXXXXXX?text=EMERGENCY:LT-2025-XXXXX  │
└─────────────────────────────────────────────────────────────────┘

When tapped:
1. Phone reads NFC tag
2. Opens WhatsApp with pre-filled message
3. User sends message (or auto-send on some devices)
4. WhatsApp webhook receives emergency trigger
5. System activates emergency response
```

### 6. QR Code Structure

```
QR Code Content:
┌─────────────────────────────────────────────────────────────────┐
│ https://wa.me/263XXXXXXXXX?text=EMERGENCY:LT-2025-XXXXX        │
└─────────────────────────────────────────────────────────────────┘

Alternative (for web fallback):
┌─────────────────────────────────────────────────────────────────┐
│ https://lifetap.co.zw/emergency/LT-2025-XXXXX                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

```bash
# Supabase
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# WhatsApp Graph API
WHATSAPP_PHONE_NUMBER_ID=<phone-number-id>
WHATSAPP_BUSINESS_ACCOUNT_ID=<business-account-id>
WHATSAPP_ACCESS_TOKEN=<access-token>
WHATSAPP_WEBHOOK_VERIFY_TOKEN=<verify-token>

# Paynow
PAYNOW_INTEGRATION_ID=<integration-id>
PAYNOW_INTEGRATION_KEY=<integration-key>

# Android SMS Gateway
SMS_GATEWAY_URL=https://<your-gateway-host>
SMS_GATEWAY_API_KEY=<api-key>

# Google Maps
GOOGLE_MAPS_API_KEY=<api-key>

# Application
APP_URL=https://lifetap.co.zw
EMERGENCY_WHATSAPP_NUMBER=263XXXXXXXXX
```

---

## Realtime Subscriptions

Supabase Realtime will be used for:

```typescript
// 1. Incident tracking (for NOK and admin)
supabase
  .channel('incident-updates')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'incidents',
    filter: `id=eq.${incidentId}`
  }, (payload) => {
    // Update UI with new status, ETA, etc.
  })
  .subscribe();

// 2. Admin dashboard live updates
supabase
  .channel('admin-incidents')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'incidents'
  }, (payload) => {
    // Update dashboard
  })
  .subscribe();

// 3. Provider dispatch notifications
supabase
  .channel('provider-dispatch')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'incidents',
    filter: `provider_id=eq.${providerId}`
  }, (payload) => {
    // Alert provider of new dispatch
  })
  .subscribe();
```

---

## Row Level Security (RLS) Policies

```sql
-- Members can only see their own data
CREATE POLICY "Members can view own profile"
ON members FOR SELECT
USING (auth.uid() = id);

-- EMR tiered access
CREATE POLICY "EMR summary access during emergency"
ON emr_records FOR SELECT
USING (
  -- Member can see their own
  auth.uid() = member_id
  OR
  -- System can access during active emergency
  EXISTS (
    SELECT 1 FROM incidents
    WHERE incidents.member_id = emr_records.member_id
    AND incidents.status IN ('activated', 'dispatched', 'en_route')
  )
);

-- Providers can only see their assigned incidents
CREATE POLICY "Providers see assigned incidents"
ON incidents FOR SELECT
USING (
  provider_id IN (
    SELECT id FROM ambulance_providers
    WHERE user_id = auth.uid()
  )
);
```

---

## Project Structure

```
lifetap/
├── supabase/
│   ├── migrations/           # Database migrations
│   │   ├── 001_members.sql
│   │   ├── 002_subscriptions.sql
│   │   ├── 003_emr.sql
│   │   ├── 004_incidents.sql
│   │   ├── 005_payments.sql
│   │   ├── 006_claims.sql
│   │   ├── 007_notifications.sql
│   │   └── 008_rls_policies.sql
│   ├── functions/            # Edge Functions
│   │   ├── _shared/          # Shared utilities
│   │   │   ├── supabase.ts
│   │   │   ├── whatsapp.ts
│   │   │   ├── paynow.ts
│   │   │   ├── sms.ts
│   │   │   ├── maps.ts
│   │   │   └── types.ts
│   │   ├── whatsapp-webhook/
│   │   ├── whatsapp-send/
│   │   ├── emergency-activate/
│   │   ├── verify-token/
│   │   ├── paynow-initiate/
│   │   ├── paynow-callback/
│   │   ├── sms-send/
│   │   ├── member-register/
│   │   └── ...
│   ├── seed.sql              # Test data
│   └── config.toml           # Supabase config
├── admin-portal/             # React/Next.js admin dashboard
│   ├── src/
│   └── ...
├── provider-portal/          # Provider web app (optional)
│   ├── src/
│   └── ...
├── docs/
│   ├── SYSTEM_DESIGN.md
│   ├── TECH_STACK.md
│   └── API.md
├── .env.example
└── README.md
```

---

## Next Steps

1. **Connect Supabase MCP** - You'll provide access
2. **Create database migrations** - Set up all tables
3. **Implement Edge Functions** - Starting with emergency flow
4. **Set up WhatsApp Graph API** - Webhook and sending
5. **Integrate Paynow** - Payment processing
6. **Configure SMS Gateway** - Fallback notifications
7. **Build Admin Portal** - Management dashboard

Ready to start when you connect the Supabase MCP!
