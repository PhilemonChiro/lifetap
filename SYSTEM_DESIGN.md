# LifeTap Medical Emergency Response System

## Complete System Design & Implementation Guide

**Version:** 1.0
**Date:** December 2025
**Prepared for:** PerformSoft Health (Private) Limited

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Analysis](#2-problem-analysis)
3. [Solution Overview](#3-solution-overview)
4. [User Journey Analysis](#4-user-journey-analysis)
5. [Edge Cases & Error Handling](#5-edge-cases--error-handling)
6. [Security Model](#6-security-model)
7. [Integration Architecture](#7-integration-architecture)
8. [Detailed System Design](#8-detailed-system-design)
9. [Database Schema](#9-database-schema)
10. [API Specifications](#10-api-specifications)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [MVP Recommendation](#12-mvp-recommendation)
13. [Technical Stack](#13-technical-stack)

---

## 1. Executive Summary

### The Problem

In Zimbabwe, over 90% of the population lacks formal medical insurance. When a road traffic accident occurs, the critical **Golden Hour** - the first 60 minutes when emergency intervention can mean the difference between life and death - is routinely lost to a single question: **Who will pay?**

Private ambulance services face an agonizing choice. They cannot verify payment while victims lie bleeding. The result: delayed dispatch, refused transport, and preventable deaths.

### The Solution

**LifeTap** is a micro-insurance-backed Emergency Response Card designed for Zimbabwe. It transforms a simple NFC card into an instant payment guarantee and medical information gateway:

- Instantly verifies coverage to ambulance providers via secure digital token
- Relays critical EMR to first responders
- Automatically notifies Next of Kin with GPS location
- Eliminates all cost barriers for bystanders and NOK at rescue point

By leveraging WhatsApp and mobile money (EcoCash/Innbucks), LifeTap delivers enterprise-grade emergency response to the informal sector majority from just **$1.00/month**.

---

## 2. Problem Analysis

### The Golden Hour Payment Paradox

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    THE GOLDEN HOUR PAYMENT PARADOX                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ACCIDENT OCCURS                                                       │
│        │                                                                │
│        ▼                                                                │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │  Bystander calls ambulance                              │          │
│   └─────────────────────┬───────────────────────────────────┘          │
│                         │                                               │
│                         ▼                                               │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │  Ambulance asks: "Who will pay?"                        │          │
│   └─────────────────────┬───────────────────────────────────┘          │
│                         │                                               │
│         ┌───────────────┴───────────────┐                              │
│         │                               │                              │
│         ▼                               ▼                              │
│   ┌───────────┐                   ┌───────────┐                        │
│   │ Can Pay   │                   │ Can't Pay │                        │
│   │ (10%)     │                   │ (90%)     │                        │
│   └─────┬─────┘                   └─────┬─────┘                        │
│         │                               │                              │
│         ▼                               ▼                              │
│   ┌───────────┐                   ┌───────────────────┐                │
│   │ Dispatch  │                   │ Delayed/Refused   │                │
│   └───────────┘                   │ = PREVENTABLE     │                │
│                                   │   DEATHS          │                │
│                                   └───────────────────┘                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Statistics

| Metric | Value |
|--------|-------|
| Population without medical insurance | 90%+ |
| WhatsApp penetration (smartphone users) | 96% |
| Mobile money usage (daily) | 85%+ |
| Target addressable market | 14 million |

---

## 3. Solution Overview

### Three Pillars Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LIFETAP ECOSYSTEM                           │
├─────────────────┬─────────────────────┬─────────────────────────┤
│   PHYSICAL      │      DIGITAL        │       FINANCIAL         │
│   INTERFACE     │      BRAIN          │       BACKBONE          │
├─────────────────┼─────────────────────┼─────────────────────────┤
│  NFC/QR Card    │  WhatsApp Chatbot   │   Micro-Insurance       │
│  - NFC Chip     │  - GPS Capture      │   - Payment Tokens      │
│  - QR Fallback  │  - NOK Alerts       │   - Tiered Coverage     │
│  - Member ID    │  - EMR Delivery     │   - Claims Settlement   │
│  - Emergency #  │  - Multilingual     │   - Fatal Payouts       │
└─────────────────┴─────────────────────┴─────────────────────────┘
```

### Product Tiers

| Tier | Price/Month | Core Coverage | Key Features |
|------|-------------|---------------|--------------|
| **Lifeline** | $1.00 | 100% Road Ambulance Transport | Essential EMR, Basic Tele-Counselling (1 Session) |
| **Guardian** | $2.50 | 100% Road/Air Stabilization | Full EMR, Trauma Counselling (2 Sessions), Live Tracking, $100 Fatal Payout |
| **Shield Plus** | $5.00 | 100% Road/Air + Transfer + $75 Emergency Fund | All Guardian + 1 GP Tele-Consult/Month, Rehab Counselling (4 Sessions), $300 Fatal Payout |

### Emergency Response Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EMERGENCY RESPONSE FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

BYSTANDER              SYSTEM                         PROVIDERS
    │                     │                               │
    │ 1. Tap NFC/QR       │                               │
    ├────────────────────>│                               │
    │                     │ 2. Capture GPS                │
    │                     │ 3. Validate Subscription      │
    │                     │ 4. Generate Payment Token     │
    │                     ├──────────────────────────────>│
    │                     │    Dispatch + EMR             │
    │                     │                               │
    │                     │ 5. Notify NOK                 │
    │                     ├──────> [Family]               │
    │                     │                               │
    │                     │ 6. Full EMR to Paramedics     │
    │                     ├──────────────────────────────>│
    │                     │                               │
    │<────────────────────┤                               │
    │  "Ambulance ETA:    │                               │
    │   12 minutes"       │                               │
```

---

## 4. User Journey Analysis

### Journey 1: Member Registration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REGISTRATION FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

Option A: USSD Registration (*151# > LifeTap)
─────────────────────────────────────────────
User dials *151#
    │
    ├──> Select "LifeTap"
    ├──> Enter Name
    ├──> Enter National ID
    ├──> Select Tier (1=Lifeline $1, 2=Guardian $2.50, 3=Shield Plus $5)
    ├──> Confirm Payment (auto-deduct from EcoCash/Innbucks)
    ├──> Receive SMS with Member ID
    └──> Card delivered via agent network OR collect at market activation

Option B: WhatsApp Registration
───────────────────────────────
User messages LifeTap WhatsApp number
    │
    ├──> Chatbot guides through registration
    ├──> Collects: Name, ID, NOK details, basic EMR
    ├──> Sends payment link (EcoCash/Innbucks)
    ├──> On payment confirmation:
    │       ├──> Generate Member ID
    │       ├──> Issue digital card (QR code image)
    │       └──> Schedule physical card delivery
    └──> Prompt to complete full EMR profile

Option C: Field Agent Registration (Market Activations)
───────────────────────────────────────────────────────
Agent at Mbare Musika/Copacabana
    │
    ├──> Agent app captures user details
    ├──> User pays via mobile money
    ├──> Instant card printing/issuance
    └──> Agent earns commission
```

### Journey 2: Emergency Activation (Critical Path)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     EMERGENCY ACTIVATION FLOW                           │
│                        (Target: < 60 seconds)                           │
└─────────────────────────────────────────────────────────────────────────┘

SECOND 0: Accident occurs. Victim unconscious. Bystander finds LifeTap card.

SECONDS 1-5: Activation
───────────────────────
Bystander taps NFC OR scans QR code
    │
    ├──> NFC: Opens WhatsApp with pre-filled message
    │         "wa.me/263XXXXXXX?text=EMERGENCY:LT-2025-A7X9K3"
    │
    └──> QR: Same deep link, fallback to web portal if no WhatsApp

SECONDS 5-15: Location & Verification
─────────────────────────────────────
WhatsApp Chatbot receives message
    │
    ├──> Instantly responds: "EMERGENCY DETECTED. Share location now."
    ├──> Bystander shares location (WhatsApp location feature)
    │
    ├──> Backend parallel processing:
    │       ├──> Verify member subscription status
    │       ├──> Check tier level
    │       ├──> Generate Guaranteed Payment Token (GPT)
    │       └──> Identify nearest ambulance provider
    │
    └──> If subscription INVALID:
            ├──> Still capture location
            ├──> Offer emergency pay-on-demand option
            └──> Connect to public emergency services

SECONDS 15-30: Dispatch
───────────────────────
System dispatches to ambulance provider
    │
    ├──> API call to provider system:
    │       {
    │         "token": "LT-2025-A7X9K3",
    │         "gps": { "lat": -17.8292, "lng": 31.0522 },
    │         "tier": "guardian",
    │         "emr_summary": {
    │           "blood_type": "O+",
    │           "allergies": ["Penicillin"],
    │           "conditions": ["Diabetes Type 2"]
    │         }
    │       }
    │
    ├──> Provider confirms dispatch
    └──> System receives ETA

SECONDS 30-45: Notifications
────────────────────────────
Parallel notifications sent:
    │
    ├──> To Bystander (WhatsApp):
    │       "Ambulance dispatched. ETA: 12 minutes.
    │        Driver: John M. | Vehicle: HAR-1234
    │        Track: [live link]"
    │
    ├──> To Next of Kin (WhatsApp/SMS):
    │       "ALERT: [Member Name] has had an emergency.
    │        Location: [Google Maps link]
    │        Ambulance ETA: 12 minutes
    │        Updates will follow."
    │
    └──> To Member (if conscious, via WhatsApp):
            "Help is on the way. ETA: 12 minutes."

SECONDS 45-60: EMR Handoff
──────────────────────────
Paramedic acknowledges dispatch
    │
    ├──> System verifies paramedic credentials
    ├──> Full EMR transmitted based on tier:
    │       ├──> Lifeline: Basic (blood type, allergies, emergency contact)
    │       ├──> Guardian: + Chronic conditions, medications, surgeries
    │       └──> Shield Plus: + Imaging refs, lab summaries, specialist notes
    │
    └──> Access logged for audit compliance
```

### Journey 3: Post-Emergency Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      POST-EMERGENCY FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

INCIDENT COMPLETION
───────────────────
Ambulance delivers patient to hospital
    │
    ├──> Paramedic marks incident "completed" in provider app
    ├──> System captures:
    │       ├──> Pickup time
    │       ├──> Delivery time
    │       ├──> Hospital delivered to
    │       └──> Basic incident notes
    │
    └──> Incident status updated across all parties

CLAIMS SETTLEMENT (48-72 hours)
───────────────────────────────
Provider submits claim
    │
    ├──> Claim includes:
    │       ├──> Payment Token (GPT)
    │       ├──> Service rendered (road transport, air evac, etc.)
    │       ├──> Distance/time
    │       └──> Supporting documentation
    │
    ├──> System auto-validates:
    │       ├──> Token authenticity
    │       ├──> Member tier covers service
    │       ├──> No duplicate claims
    │       └──> Service matches incident record
    │
    ├──> If Shield Plus: Process $75 stabilization fund to hospital
    │
    └──> Settlement via bank transfer to provider

NOK FOLLOW-UP
─────────────
24 hours post-incident:
    │
    ├──> Automated check-in to NOK
    ├──> Patient status inquiry
    └──> Counselling session scheduling prompt

COUNSELLING ACTIVATION
──────────────────────
Based on tier:
    │
    ├──> Lifeline: 1 session offered within 72 hours
    ├──> Guardian: 2 sessions, family can join
    └──> Shield Plus: 4 sessions, rehabilitation focus

Sessions booked via WhatsApp chatbot
Conducted via WhatsApp video call
```

---

## 5. Edge Cases & Error Handling

### Critical Edge Cases

| Scenario | Handling |
|----------|----------|
| **Subscription expired** | Allow emergency activation, flag for post-incident payment, or offer instant renewal |
| **No GPS permission** | Request address manually, use cell tower triangulation as fallback |
| **No ambulance available** | Escalate to secondary providers, notify public emergency services, inform bystander |
| **Bystander phone has no data** | QR code links to USSD fallback (*151*EMERGENCY*MEMBERID#) |
| **Multiple activations same member** | Detect duplicate within 30 min window, confirm with bystander |
| **Provider API down** | Fallback to USSD verification, manual dispatch via call center |
| **WhatsApp API rate limited** | Queue with priority, SMS fallback for critical messages |
| **Fraudulent activation** | Post-incident review, member notified, pattern detection |
| **Mass casualty event** | Bulk activation mode, reinsurance triggers, capacity management |
| **Member deceased** | Fatal accident payout process, sensitive NOK communication |

### Subscription Edge Cases

```
GRACE PERIOD LOGIC
──────────────────
Subscription expires on 15th
    │
    ├──> Day 15-17: 48-hour grace period
    │       ├──> Full service maintained
    │       └──> Renewal reminders sent
    │
    ├──> Day 18-22: Restricted period
    │       ├──> Emergency activation still works
    │       ├──> Flagged for immediate renewal
    │       └──> Post-incident billing if not renewed
    │
    └──> Day 23+: Lapsed
            ├──> Card deactivated
            ├──> Re-registration required
            └──> Historical EMR preserved for 12 months
```

---

## 6. Security Model

### Data Classification

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA SENSITIVITY LEVELS                          │
├─────────────────┬───────────────────┬───────────────────────────────────┤
│ LEVEL           │ DATA TYPE         │ ACCESS CONTROL                    │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ PUBLIC          │ Member ID format  │ Anyone (on card)                  │
│                 │ Emergency hotline │                                   │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ INTERNAL        │ Subscription      │ System, Admin, Provider (limited) │
│                 │ status, Tier      │                                   │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ CONFIDENTIAL    │ Name, NOK details │ Member, Admin, Verified Provider  │
│                 │ Basic EMR         │                                   │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ HIGHLY          │ Full EMR, Medical │ Member, Verified Medical Staff    │
│ CONFIDENTIAL    │ history, Labs     │ (with audit log)                  │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ RESTRICTED      │ Payment details,  │ System only, encrypted at rest    │
│                 │ National ID       │                                   │
└─────────────────┴───────────────────┴───────────────────────────────────┘
```

### Access Control Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ROLE-BASED ACCESS CONTROL                           │
├──────────────────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────┤
│ RESOURCE         │MEMBER│BYSTND│PARMED│PROVDR│ADMIN │SYSTEM│COUNSELLOR │
├──────────────────┼──────┼──────┼──────┼──────┼──────┼──────┼───────────┤
│ Own Profile      │ CRUD │  -   │  -   │  -   │  R   │ CRUD │     -     │
│ Own EMR          │ CRUD │  -   │  -   │  -   │  R   │  R   │     -     │
│ Basic EMR (emerg)│  R   │  R*  │  R   │  R   │  R   │  R   │     -     │
│ Full EMR (emerg) │  R   │  -   │  R** │  -   │  R   │  R   │     -     │
│ Payment Token    │  -   │  R   │  R   │  R   │  R   │ CRUD │     -     │
│ Incident Records │  R   │  -   │  R   │  R   │ CRUD │ CRUD │     R     │
│ Claims           │  R   │  -   │  -   │ CRUD │ CRUD │  R   │     -     │
│ NOK Details      │ CRUD │  -   │  R   │  -   │  R   │  R   │     -     │
│ Session Notes    │  R   │  -   │  -   │  -   │  -   │  -   │   CRUD    │
└──────────────────┴──────┴──────┴──────┴──────┴──────┴──────┴───────────┘

* During active emergency only
** Requires credential verification + tier authorization
```

### Encryption Strategy

```
AT REST:
├── Database: AES-256 encryption (AWS RDS/Azure SQL encryption)
├── EMR Fields: Application-level encryption with rotating keys
├── Backups: Encrypted with separate key hierarchy
└── Logs: PII redacted, encrypted storage

IN TRANSIT:
├── All APIs: TLS 1.3 mandatory
├── WhatsApp: End-to-end (platform provided)
├── Mobile Money: Provider's encryption + our TLS
└── Inter-service: mTLS in production

KEY MANAGEMENT:
├── AWS KMS / Azure Key Vault
├── Automatic rotation (90 days)
├── Separate keys per data classification
└── HSM for payment token signing
```

---

## 7. Integration Architecture

### External System Integrations

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                              │
└─────────────────────────────────────────────────────────────────────────┘

1. WHATSAPP BUSINESS API
   ├── Provider: 360dialog / Twilio / Direct Meta
   ├── Capabilities needed:
   │     ├── Send/receive messages
   │     ├── Location sharing
   │     ├── Media (images, documents)
   │     ├── Interactive buttons/lists
   │     └── Video calls (for counselling)
   ├── Rate limits: ~80 messages/second (business tier)
   └── Fallback: SMS via Twilio/Africa's Talking

2. ECOCASH API
   ├── Integration type: Merchant API
   ├── Capabilities:
   │     ├── Payment collection (C2B)
   │     ├── Disbursement (B2C) - for claims
   │     ├── Auto-deduction (recurring)
   │     └── Balance inquiry
   ├── Settlement: T+1
   └── Fallback: Paynow aggregator

3. INNBUCKS API
   ├── Similar to EcoCash
   ├── Growing user base
   └── Lower transaction fees

4. AMBULANCE PROVIDER SYSTEMS
   ├── Integration options:
   │     ├── REST API (preferred)
   │     ├── USSD verification (fallback)
   │     └── SMS dispatch (legacy)
   ├── Required endpoints:
   │     ├── POST /dispatch - request ambulance
   │     ├── GET /status/{incident_id} - track
   │     ├── POST /verify-token - validate GPT
   │     └── POST /complete - mark done
   └── Webhook: Status updates

5. USSD GATEWAY (for non-smartphone users)
   ├── Provider: Local telco partnership
   ├── Capabilities:
   │     ├── Registration
   │     ├── Subscription management
   │     ├── Emergency activation (fallback)
   │     └── Balance/status check
   └── Integration: USSD gateway API

6. SMS GATEWAY
   ├── Provider: Africa's Talking / Twilio
   ├── Use cases:
   │     ├── NOK notifications (non-WhatsApp)
   │     ├── OTP verification
   │     ├── Subscription reminders
   │     └── Emergency fallback
   └── Delivery reports: Required

7. MAPPING/GEOLOCATION
   ├── Google Maps API:
   │     ├── Geocoding (address to coords)
   │     ├── Reverse geocoding
   │     ├── Distance matrix (ETA calculation)
   │     └── Static maps (for sharing)
   └── Fallback: OpenStreetMap
```

---

## 8. Detailed System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              LIFETAP SYSTEM ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────┐
                                    │   CLIENTS   │
                                    └──────┬──────┘
                                           │
            ┌──────────────────────────────┼──────────────────────────────┐
            │                              │                              │
            ▼                              ▼                              ▼
    ┌───────────────┐            ┌─────────────────┐            ┌─────────────────┐
    │  NFC/QR Card  │            │ WhatsApp Users  │            │   Admin Portal  │
    │   (Physical)  │            │   (Bystander,   │            │   (Web App)     │
    └───────┬───────┘            │  Member, NOK)   │            └────────┬────────┘
            │                    └────────┬────────┘                     │
            │                             │                              │
            │    ┌────────────────────────┼────────────────────────┐     │
            │    │                        ▼                        │     │
            │    │              ┌─────────────────┐                │     │
            │    │              │  API GATEWAY    │                │     │
            │    │              │  (Kong/AWS)     │◄───────────────┼─────┘
            │    │              │  - Rate Limit   │                │
            │    │              │  - Auth         │                │
            │    │              │  - Routing      │                │
            │    │              └────────┬────────┘                │
            │    │                       │                         │
            │    │    ┌──────────────────┼──────────────────┐      │
            │    │    │                  │                  │      │
            │    │    ▼                  ▼                  ▼      │
            │    │ ┌──────────┐   ┌────────────┐   ┌────────────┐  │
            │    │ │ MEMBER   │   │ EMERGENCY  │   │  PAYMENT   │  │
            │    │ │ SERVICE  │   │  SERVICE   │   │  SERVICE   │  │
            │    │ └────┬─────┘   └─────┬──────┘   └─────┬──────┘  │
            │    │      │               │                │         │
            │    │      │    ┌──────────┼────────────────┼─────┐   │
            │    │      │    │          │                │     │   │
            │    │      ▼    ▼          ▼                ▼     │   │
            │    │   ┌─────────────────────────────────────┐   │   │
            │    │   │           MESSAGE QUEUE             │   │   │
            │    │   │         (RabbitMQ / SQS)            │   │   │
            │    │   └──────────────────┬──────────────────┘   │   │
            │    │                      │                      │   │
            │    │    ┌─────────────────┼─────────────────┐    │   │
            │    │    │                 │                 │    │   │
            │    │    ▼                 ▼                 ▼    │   │
            │    │ ┌──────────┐  ┌────────────┐  ┌──────────┐  │   │
            │    │ │   EMR    │  │NOTIFICATION│  │  CLAIMS  │  │   │
            │    │ │ SERVICE  │  │  SERVICE   │  │ SERVICE  │  │   │
            │    │ └────┬─────┘  └─────┬──────┘  └────┬─────┘  │   │
            │    │      │              │              │        │   │
            │    └──────┼──────────────┼──────────────┼────────┘   │
            │           │              │              │            │
            │           ▼              ▼              ▼            │
            │    ┌─────────────────────────────────────────────┐   │
            │    │              DATA LAYER                     │   │
            │    │  ┌──────────┐ ┌───────┐ ┌────────────────┐  │   │
            │    │  │PostgreSQL│ │ Redis │ │ Object Storage │  │   │
            │    │  │ (Primary)│ │(Cache)│ │ (S3/Blob)      │  │   │
            │    │  └──────────┘ └───────┘ └────────────────┘  │   │
            │    └─────────────────────────────────────────────┘   │
            │                                                      │
            │              EXTERNAL INTEGRATIONS                   │
            │    ┌─────────────────────────────────────────────┐   │
            │    │ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │   │
            └────┼─│WhatsApp │ │ EcoCash │ │Ambulance APIs   │─┼───┘
                 │ │   API   │ │Innbucks │ │                 │ │
                 │ └─────────┘ └─────────┘ └─────────────────┘ │
                 └─────────────────────────────────────────────┘
```

### Microservices Breakdown

#### 1. Member Service (`member-service`)

```
Responsibilities:
├── Member registration & KYC
├── Profile management
├── Subscription lifecycle
├── Card issuance tracking
└── NOK management

Database: members, subscriptions, cards, next_of_kin

Events Published:
├── member.registered
├── subscription.activated
├── subscription.expired
└── subscription.renewed

API Endpoints:
POST   /members
GET    /members/{id}
PUT    /members/{id}
POST   /members/{id}/subscribe
GET    /members/{id}/subscription
POST   /members/{id}/nok
GET    /members/verify/{member_id}  (public - for emergency)
```

#### 2. EMR Service (`emr-service`)

```
Responsibilities:
├── Medical record CRUD
├── Tiered access control
├── Encryption/decryption
├── Audit logging
└── Document storage refs

Database: emr_records, emr_access_logs, documents

Events Published:
├── emr.updated
└── emr.accessed

API Endpoints:
GET    /emr/{member_id}              (full - authorized)
GET    /emr/{member_id}/summary      (for dispatch)
PUT    /emr/{member_id}
POST   /emr/{member_id}/documents
GET    /emr/{member_id}/access-log
```

#### 3. Emergency Service (`emergency-service`)

```
Responsibilities:
├── Emergency activation
├── GPS processing
├── Payment token generation
├── Provider selection
├── Dispatch orchestration
└── Incident tracking

Database: incidents, payment_tokens, dispatch_logs

Events Published:
├── emergency.activated
├── emergency.dispatched
├── emergency.provider_assigned
└── emergency.completed

API Endpoints:
POST   /emergency/activate
GET    /emergency/{incident_id}
PUT    /emergency/{incident_id}/status
GET    /emergency/{incident_id}/track
POST   /emergency/verify-token       (for providers)
```

#### 4. Payment Service (`payment-service`)

```
Responsibilities:
├── Mobile money integration
├── Subscription billing
├── Payment verification
├── Disbursements
└── Transaction history

Database: transactions, payment_methods, disbursements

Events Published:
├── payment.received
├── payment.failed
└── disbursement.completed

API Endpoints:
POST   /payments/initiate
GET    /payments/{transaction_id}
POST   /payments/callback/ecocash
POST   /payments/callback/innbucks
POST   /disbursements
```

#### 5. Notification Service (`notification-service`)

```
Responsibilities:
├── WhatsApp message sending
├── SMS fallback
├── NOK alerts
├── Template management
└── Delivery tracking

Database: notifications, templates, delivery_logs

Events Consumed:
├── emergency.activated -> NOK alert
├── emergency.dispatched -> Bystander update
├── subscription.expiring -> Reminder
└── payment.received -> Confirmation

API Endpoints:
POST   /notifications/send
GET    /notifications/{id}/status
POST   /notifications/whatsapp/webhook
```

#### 6. Claims Service (`claims-service`)

```
Responsibilities:
├── Claim submission
├── Validation
├── Settlement processing
├── Provider management
└── Reporting

Database: claims, providers, settlements

Events Published:
├── claim.submitted
├── claim.validated
└── claim.settled

API Endpoints:
POST   /claims
GET    /claims/{id}
PUT    /claims/{id}/validate
POST   /claims/{id}/settle
GET    /providers
POST   /providers
```

#### 7. Chatbot Service (`chatbot-service`)

```
Responsibilities:
├── WhatsApp conversation management
├── Intent recognition
├── Registration flows
├── Emergency flow handling
├── Multilingual support
└── Session management

Database: conversations, sessions

Events Published:
├── chatbot.emergency_detected
└── chatbot.registration_completed

Integrations:
- WhatsApp Business API
- Member Service
- Emergency Service
- EMR Service
```

#### 8. Admin Service (`admin-service`)

```
Responsibilities:
├── Dashboard APIs
├── Reporting
├── User management
├── Audit logs
└── System configuration

Database: admin_users, audit_logs, reports

API Endpoints:
GET    /admin/dashboard/stats
GET    /admin/members
GET    /admin/incidents
GET    /admin/claims
GET    /admin/reports/*
POST   /admin/users
```

---

## 9. Database Schema

### Member Service Schema

```sql
-- =====================================================
-- MEMBER SERVICE SCHEMA
-- =====================================================

CREATE TABLE members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id VARCHAR(20) UNIQUE NOT NULL,  -- LT-2025-XXXXX format

    -- Personal Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    national_id_encrypted BYTEA NOT NULL,  -- AES-256 encrypted
    national_id_hash VARCHAR(64) NOT NULL, -- For lookup without decryption
    phone_number VARCHAR(20) NOT NULL,
    phone_number_verified BOOLEAN DEFAULT FALSE,
    email VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(10),

    -- Address
    address_line1 VARCHAR(255),
    address_city VARCHAR(100),
    address_province VARCHAR(100),

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, suspended, lapsed
    kyc_status VARCHAR(20) DEFAULT 'pending',

    -- Metadata
    registration_channel VARCHAR(50), -- ussd, whatsapp, agent, web
    registration_agent_id UUID,
    language_preference VARCHAR(10) DEFAULT 'en', -- en, sn, nd

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES members(id),

    tier VARCHAR(20) NOT NULL, -- lifeline, guardian, shield_plus
    price_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    status VARCHAR(20) NOT NULL, -- active, grace_period, restricted, expired, cancelled

    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    grace_period_ends_at TIMESTAMP WITH TIME ZONE,

    auto_renew BOOLEAN DEFAULT TRUE,
    payment_method_id UUID,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES members(id),

    card_number VARCHAR(20) UNIQUE NOT NULL,
    nfc_uid VARCHAR(32) UNIQUE,
    qr_code_hash VARCHAR(64) UNIQUE NOT NULL,

    status VARCHAR(20) DEFAULT 'pending', -- pending, active, lost, replaced

    issued_at TIMESTAMP WITH TIME ZONE,
    activated_at TIMESTAMP WITH TIME ZONE,
    deactivated_at TIMESTAMP WITH TIME ZONE,

    issued_by_agent_id UUID,
    delivery_address VARCHAR(500),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE next_of_kin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES members(id),

    full_name VARCHAR(200) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255),

    is_primary BOOLEAN DEFAULT FALSE,
    notification_preference VARCHAR(20) DEFAULT 'whatsapp', -- whatsapp, sms, both

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### EMR Service Schema

```sql
-- =====================================================
-- EMR SERVICE SCHEMA
-- =====================================================

CREATE TABLE emr_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL UNIQUE,

    -- Basic (Lifeline tier)
    blood_type VARCHAR(5),
    allergies JSONB DEFAULT '[]',
    emergency_notes TEXT,

    -- Extended (Guardian tier)
    chronic_conditions JSONB DEFAULT '[]',
    current_medications JSONB DEFAULT '[]',
    past_surgeries JSONB DEFAULT '[]',
    primary_physician_name VARCHAR(200),
    primary_physician_phone VARCHAR(20),

    -- Premium (Shield Plus tier)
    specialist_consultations JSONB DEFAULT '[]',

    -- Encrypted sensitive data
    detailed_history_encrypted BYTEA,

    -- Metadata
    last_updated_by UUID,
    data_completeness_score INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE emr_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_id UUID NOT NULL REFERENCES emr_records(id),

    document_type VARCHAR(50) NOT NULL, -- lab_result, imaging, prescription, report
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- S3/Blob path
    file_size_bytes INTEGER,
    mime_type VARCHAR(100),

    description TEXT,
    document_date DATE,

    uploaded_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE emr_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_id UUID NOT NULL REFERENCES emr_records(id),

    accessed_by_id UUID NOT NULL,
    accessed_by_role VARCHAR(50) NOT NULL, -- member, paramedic, admin, system
    access_type VARCHAR(50) NOT NULL, -- view_summary, view_full, update, download

    incident_id UUID, -- If accessed during emergency
    ip_address INET,
    user_agent TEXT,

    data_accessed JSONB, -- Which fields were accessed

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Emergency Service Schema

```sql
-- =====================================================
-- EMERGENCY SERVICE SCHEMA
-- =====================================================

CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_number VARCHAR(30) UNIQUE NOT NULL, -- INC-2025-XXXXX

    member_id UUID NOT NULL,
    member_tier VARCHAR(20) NOT NULL,

    -- Activation
    activated_by_phone VARCHAR(20), -- Bystander's phone
    activation_method VARCHAR(20) NOT NULL, -- nfc, qr, ussd, manual

    -- Location
    gps_latitude DECIMAL(10, 8),
    gps_longitude DECIMAL(11, 8),
    gps_accuracy_meters DECIMAL(10, 2),
    address_description TEXT,

    -- Status tracking
    status VARCHAR(30) NOT NULL, -- activated, verified, dispatching, dispatched,
                                  -- en_route, arrived, transporting, completed, cancelled

    -- Provider assignment
    provider_id UUID,
    ambulance_vehicle_id VARCHAR(50),
    paramedic_name VARCHAR(200),
    paramedic_phone VARCHAR(20),

    -- Timing
    activated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    dispatched_at TIMESTAMP WITH TIME ZONE,
    provider_acknowledged_at TIMESTAMP WITH TIME ZONE,
    arrived_at TIMESTAMP WITH TIME ZONE,
    transport_started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Destination
    destination_hospital VARCHAR(200),
    destination_address TEXT,

    -- ETA
    initial_eta_minutes INTEGER,

    -- Payment
    payment_token_id UUID,

    -- Notes
    incident_notes TEXT,
    completion_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE payment_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_code VARCHAR(20) UNIQUE NOT NULL, -- LT-2025-A7X9K3 format

    incident_id UUID REFERENCES incidents(id),
    member_id UUID NOT NULL,
    subscription_id UUID NOT NULL,

    -- Coverage
    tier VARCHAR(20) NOT NULL,
    max_coverage_cents INTEGER NOT NULL,
    services_covered JSONB NOT NULL, -- ['road_ambulance', 'air_ambulance', 'stabilization']

    -- Status
    status VARCHAR(20) NOT NULL, -- active, used, expired, cancelled

    -- Verification
    verified_by_provider_id UUID,
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Validity
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE incident_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id UUID NOT NULL REFERENCES incidents(id),

    from_status VARCHAR(30),
    to_status VARCHAR(30) NOT NULL,

    changed_by_id UUID,
    changed_by_type VARCHAR(30), -- system, provider, admin

    notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Payment Service Schema

```sql
-- =====================================================
-- PAYMENT SERVICE SCHEMA
-- =====================================================

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL,

    provider VARCHAR(30) NOT NULL, -- ecocash, innbucks, bank
    account_identifier_encrypted BYTEA NOT NULL,
    account_identifier_masked VARCHAR(50), -- ****1234

    is_default BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_ref VARCHAR(50) UNIQUE NOT NULL,

    member_id UUID NOT NULL,
    payment_method_id UUID,

    type VARCHAR(30) NOT NULL, -- subscription, renewal, on_demand
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    provider VARCHAR(30) NOT NULL,
    provider_ref VARCHAR(100),

    status VARCHAR(20) NOT NULL, -- pending, processing, completed, failed, refunded
    failure_reason TEXT,

    subscription_id UUID,

    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    metadata JSONB DEFAULT '{}'
);

CREATE TABLE disbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    disbursement_ref VARCHAR(50) UNIQUE NOT NULL,

    claim_id UUID NOT NULL,
    provider_id UUID NOT NULL,

    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',

    payment_method VARCHAR(30) NOT NULL, -- bank_transfer, ecocash_business
    account_details_encrypted BYTEA NOT NULL,

    status VARCHAR(20) NOT NULL, -- pending, processing, completed, failed
    failure_reason TEXT,

    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    metadata JSONB DEFAULT '{}'
);
```

### Claims Service Schema

```sql
-- =====================================================
-- CLAIMS SERVICE SCHEMA
-- =====================================================

CREATE TABLE ambulance_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(200) NOT NULL,
    registration_number VARCHAR(50),

    -- Contact
    primary_phone VARCHAR(20) NOT NULL,
    emergency_phone VARCHAR(20),
    email VARCHAR(255),

    -- Location
    base_address TEXT,
    base_latitude DECIMAL(10, 8),
    base_longitude DECIMAL(11, 8),
    service_area_polygon JSONB, -- GeoJSON polygon

    -- Capabilities
    has_road_ambulance BOOLEAN DEFAULT TRUE,
    has_air_ambulance BOOLEAN DEFAULT FALSE,
    road_ambulance_count INTEGER DEFAULT 0,
    air_ambulance_count INTEGER DEFAULT 0,

    -- Integration
    api_endpoint VARCHAR(500),
    api_key_encrypted BYTEA,
    ussd_verification_code VARCHAR(20),
    integration_type VARCHAR(20), -- api, ussd, manual

    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, suspended
    verified_at TIMESTAMP WITH TIME ZONE,

    -- Payment
    bank_name VARCHAR(100),
    bank_account_encrypted BYTEA,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number VARCHAR(30) UNIQUE NOT NULL, -- CLM-2025-XXXXX

    incident_id UUID NOT NULL REFERENCES incidents(id),
    payment_token_id UUID NOT NULL REFERENCES payment_tokens(id),
    provider_id UUID NOT NULL REFERENCES ambulance_providers(id),
    member_id UUID NOT NULL,

    -- Service details
    service_type VARCHAR(50) NOT NULL, -- road_transport, air_transport, stabilization
    service_description TEXT,

    -- Amounts
    claimed_amount_cents INTEGER NOT NULL,
    approved_amount_cents INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',

    -- Status
    status VARCHAR(30) NOT NULL, -- submitted, under_review, approved, rejected, settled
    rejection_reason TEXT,

    -- Documents
    supporting_documents JSONB DEFAULT '[]',

    -- Timestamps
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    settled_at TIMESTAMP WITH TIME ZONE,

    reviewed_by_id UUID,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Notification Service Schema

```sql
-- =====================================================
-- NOTIFICATION SERVICE SCHEMA
-- =====================================================

CREATE TABLE notification_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(30) NOT NULL, -- whatsapp, sms
    language VARCHAR(10) NOT NULL,

    subject VARCHAR(255),
    body_template TEXT NOT NULL,

    variables JSONB DEFAULT '[]', -- Expected variables

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    recipient_phone VARCHAR(20) NOT NULL,
    recipient_member_id UUID,

    type VARCHAR(30) NOT NULL, -- whatsapp, sms
    template_id UUID REFERENCES notification_templates(id),

    content TEXT NOT NULL,

    -- Related entities
    incident_id UUID,

    -- Delivery
    status VARCHAR(20) NOT NULL, -- queued, sent, delivered, read, failed
    provider_message_id VARCHAR(100),

    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,

    failure_reason TEXT,
    retry_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Database Indexes

```sql
-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_members_phone ON members(phone_number);
CREATE INDEX idx_members_member_id ON members(member_id);
CREATE INDEX idx_members_status ON members(status);

CREATE INDEX idx_subscriptions_member_id ON subscriptions(member_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_expires_at ON subscriptions(expires_at);

CREATE INDEX idx_cards_member_id ON cards(member_id);
CREATE INDEX idx_cards_nfc_uid ON cards(nfc_uid);
CREATE INDEX idx_cards_qr_code_hash ON cards(qr_code_hash);

CREATE INDEX idx_incidents_member_id ON incidents(member_id);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_activated_at ON incidents(activated_at);
CREATE INDEX idx_incidents_provider_id ON incidents(provider_id);

CREATE INDEX idx_payment_tokens_code ON payment_tokens(token_code);
CREATE INDEX idx_payment_tokens_incident ON payment_tokens(incident_id);

CREATE INDEX idx_claims_incident_id ON claims(incident_id);
CREATE INDEX idx_claims_provider_id ON claims(provider_id);
CREATE INDEX idx_claims_status ON claims(status);

CREATE INDEX idx_notifications_recipient ON notifications(recipient_phone);
CREATE INDEX idx_notifications_incident ON notifications(incident_id);
CREATE INDEX idx_notifications_status ON notifications(status);
```

---

## 10. API Specifications

### Emergency Activation API

```yaml
POST /api/v1/emergency/activate
---
Description: Activate emergency response for a member
Rate Limit: 10/minute per IP (prevent abuse)

Request:
{
  "member_id": "LT-2025-A7X9K3",
  "activation_method": "nfc",
  "bystander_phone": "+263771234567",
  "location": {
    "latitude": -17.8292,
    "longitude": 31.0522,
    "accuracy_meters": 10
  }
}

Response (200 OK):
{
  "success": true,
  "incident": {
    "id": "uuid",
    "incident_number": "INC-2025-00001",
    "status": "dispatching",
    "member": {
      "first_name": "John",
      "tier": "guardian"
    },
    "emr_summary": {
      "blood_type": "O+",
      "allergies": ["Penicillin"],
      "critical_conditions": ["Diabetes Type 2"]
    },
    "payment_token": "LT-2025-A7X9K3",
    "tracking_url": "https://lifetap.co.zw/track/INC-2025-00001"
  },
  "next_steps": {
    "message": "Ambulance being dispatched. Stay with the patient.",
    "eta_update_in_seconds": 30
  }
}

Response (402 - Subscription Issue):
{
  "success": false,
  "error": "subscription_expired",
  "message": "Member subscription expired. Emergency activation available for $5.",
  "options": {
    "pay_now_url": "https://lifetap.co.zw/pay/emergency/uuid",
    "public_emergency": "+263242123456"
  }
}
```

### Token Verification API

```yaml
GET /api/v1/emergency/verify-token/{token_code}
---
Description: Verify payment token (for ambulance providers)
Auth: Provider API Key

Response (200 OK):
{
  "valid": true,
  "token": {
    "code": "LT-2025-A7X9K3",
    "status": "active",
    "tier": "guardian",
    "coverage": {
      "road_ambulance": true,
      "air_ambulance": true,
      "stabilization_fund": false,
      "max_amount_usd": 500
    },
    "valid_until": "2025-12-02T23:59:59Z"
  },
  "incident": {
    "id": "uuid",
    "location": {
      "latitude": -17.8292,
      "longitude": 31.0522,
      "address": "Corner Samora Machel & Julius Nyerere, Harare"
    }
  },
  "member_emr": {
    "blood_type": "O+",
    "allergies": ["Penicillin"],
    "conditions": ["Diabetes Type 2"],
    "medications": ["Metformin 500mg"]
  }
}
```

### Member Registration API

```yaml
POST /api/v1/members
---
Description: Register a new member

Request:
{
  "first_name": "John",
  "last_name": "Moyo",
  "phone_number": "+263771234567",
  "national_id": "63-123456-A-78",
  "date_of_birth": "1985-03-15",
  "gender": "male",
  "address": {
    "line1": "123 Main Street",
    "city": "Harare",
    "province": "Harare"
  },
  "next_of_kin": {
    "full_name": "Mary Moyo",
    "relationship": "spouse",
    "phone_number": "+263772345678"
  },
  "tier": "guardian",
  "payment_method": "ecocash",
  "language": "en"
}

Response (201 Created):
{
  "success": true,
  "member": {
    "id": "uuid",
    "member_id": "LT-2025-00001",
    "status": "pending_payment"
  },
  "payment": {
    "amount": 2.50,
    "currency": "USD",
    "provider": "ecocash",
    "instructions": "Dial *151*2*1*MERCHANT_CODE*2.50# to complete payment",
    "expires_in_minutes": 30
  }
}
```

### Subscription Management API

```yaml
POST /api/v1/members/{id}/subscribe
---
Description: Create or renew subscription

Request:
{
  "tier": "guardian",
  "payment_method_id": "uuid",
  "auto_renew": true
}

Response (200 OK):
{
  "success": true,
  "subscription": {
    "id": "uuid",
    "tier": "guardian",
    "status": "active",
    "started_at": "2025-12-02T00:00:00Z",
    "expires_at": "2026-01-02T00:00:00Z",
    "auto_renew": true
  }
}
```

### EMR API

```yaml
GET /api/v1/emr/{member_id}
---
Description: Get member's EMR (full - requires authorization)
Auth: Bearer token with appropriate role

Response (200 OK):
{
  "member_id": "LT-2025-00001",
  "tier_access": "guardian",
  "basic": {
    "blood_type": "O+",
    "allergies": [
      { "allergen": "Penicillin", "severity": "severe", "reaction": "anaphylaxis" }
    ],
    "emergency_contact": {
      "name": "Mary Moyo",
      "phone": "+263772345678",
      "relationship": "spouse"
    }
  },
  "extended": {
    "chronic_conditions": [
      { "condition": "Diabetes Type 2", "diagnosed_date": "2018-06-15", "status": "managed" }
    ],
    "current_medications": [
      { "name": "Metformin", "dosage": "500mg", "frequency": "twice daily" }
    ],
    "past_surgeries": [],
    "primary_physician": {
      "name": "Dr. Sarah Ncube",
      "phone": "+263242123456"
    }
  },
  "data_completeness": 75,
  "last_updated": "2025-11-15T10:30:00Z"
}

GET /api/v1/emr/{member_id}/summary
---
Description: Get EMR summary for emergency dispatch (minimal auth)

Response (200 OK):
{
  "blood_type": "O+",
  "allergies": ["Penicillin"],
  "critical_conditions": ["Diabetes Type 2"],
  "critical_medications": ["Metformin 500mg"]
}
```

### Claims API

```yaml
POST /api/v1/claims
---
Description: Submit a claim (for providers)
Auth: Provider API Key

Request:
{
  "incident_id": "uuid",
  "payment_token": "LT-2025-A7X9K3",
  "service_type": "road_transport",
  "service_description": "Emergency transport from accident scene to Parirenyatwa Hospital",
  "claimed_amount_cents": 15000,
  "currency": "USD",
  "supporting_documents": [
    {
      "type": "incident_report",
      "file_url": "https://..."
    }
  ]
}

Response (201 Created):
{
  "success": true,
  "claim": {
    "id": "uuid",
    "claim_number": "CLM-2025-00001",
    "status": "submitted",
    "estimated_settlement": "2025-12-05"
  }
}
```

---

## 11. Implementation Roadmap

### Phase 1: Project Setup & Infrastructure

| Task | Description | Priority |
|------|-------------|----------|
| 1.1 | Initialize monorepo structure (Nx/Turborepo) | High |
| 1.2 | Set up PostgreSQL database with migrations | High |
| 1.3 | Set up Redis for caching/sessions | High |
| 1.4 | Configure Docker development environment | High |
| 1.5 | Set up CI/CD pipeline (GitHub Actions) | Medium |
| 1.6 | Configure cloud infrastructure (AWS/Azure) | Medium |
| 1.7 | Set up logging & monitoring (ELK/CloudWatch) | Medium |
| 1.8 | Configure API Gateway | Medium |

### Phase 2: Core Member Management System

| Task | Description | Priority |
|------|-------------|----------|
| 2.1 | Create Member Service scaffold | High |
| 2.2 | Implement member registration API | High |
| 2.3 | Implement member ID generation (LT-XXXX format) | High |
| 2.4 | Build subscription management | High |
| 2.5 | Implement tier logic (Lifeline/Guardian/Shield Plus) | High |
| 2.6 | Create NOK (Next of Kin) management | High |
| 2.7 | Build card issuance tracking | Medium |
| 2.8 | Implement member verification endpoint (public) | High |
| 2.9 | Add KYC workflow | Medium |
| 2.10 | Build subscription expiry/grace period logic | High |

### Phase 3: EMR System

| Task | Description | Priority |
|------|-------------|----------|
| 3.1 | Create EMR Service scaffold | High |
| 3.2 | Design EMR data model with encryption | High |
| 3.3 | Implement tiered access control | High |
| 3.4 | Build EMR CRUD operations | High |
| 3.5 | Create EMR summary endpoint (for emergencies) | High |
| 3.6 | Implement document upload (S3/Blob) | Medium |
| 3.7 | Build access audit logging | High |
| 3.8 | Add EMR data completeness scoring | Low |

### Phase 4: Emergency Response System (Critical Path)

| Task | Description | Priority |
|------|-------------|----------|
| 4.1 | Create Emergency Service scaffold | Critical |
| 4.2 | Build emergency activation endpoint | Critical |
| 4.3 | Implement GPS capture & validation | Critical |
| 4.4 | Create Payment Token (GPT) generation | Critical |
| 4.5 | Build provider selection algorithm (nearest) | Critical |
| 4.6 | Implement dispatch orchestration | Critical |
| 4.7 | Create incident status tracking | Critical |
| 4.8 | Build token verification API (for providers) | Critical |
| 4.9 | Implement incident timeline/history | High |
| 4.10 | Create real-time tracking endpoint | High |
| 4.11 | Build USSD fallback for emergency | Medium |
| 4.12 | Implement duplicate activation detection | Medium |

### Phase 5: Payment & Subscription System

| Task | Description | Priority |
|------|-------------|----------|
| 5.1 | Create Payment Service scaffold | High |
| 5.2 | Integrate EcoCash API | High |
| 5.3 | Integrate Innbucks API | High |
| 5.4 | Build subscription billing logic | High |
| 5.5 | Implement auto-renewal | High |
| 5.6 | Create payment webhook handlers | High |
| 5.7 | Build disbursement system (for providers) | High |
| 5.8 | Implement transaction history | Medium |
| 5.9 | Add Paynow fallback integration | Medium |
| 5.10 | Build USSD subscription flow (*151#) | Medium |

### Phase 6: WhatsApp Chatbot Integration

| Task | Description | Priority |
|------|-------------|----------|
| 6.1 | Set up WhatsApp Business API | Critical |
| 6.2 | Create Chatbot Service scaffold | Critical |
| 6.3 | Build conversation state machine | High |
| 6.4 | Implement emergency flow handler | Critical |
| 6.5 | Build registration flow | High |
| 6.6 | Implement profile management flow | Medium |
| 6.7 | Add multilingual support (EN/SN/ND) | High |
| 6.8 | Build location sharing handler | Critical |
| 6.9 | Implement interactive buttons/lists | Medium |
| 6.10 | Create session management | High |

### Phase 7: Notification System

| Task | Description | Priority |
|------|-------------|----------|
| 7.1 | Create Notification Service scaffold | High |
| 7.2 | Build WhatsApp message sender | High |
| 7.3 | Implement SMS fallback (Africa's Talking) | High |
| 7.4 | Create notification templates | High |
| 7.5 | Build NOK alert system | Critical |
| 7.6 | Implement delivery tracking | Medium |
| 7.7 | Add retry logic for failed deliveries | Medium |
| 7.8 | Build subscription reminder system | Medium |

### Phase 8: Claims & Provider Management

| Task | Description | Priority |
|------|-------------|----------|
| 8.1 | Create Claims Service scaffold | High |
| 8.2 | Build provider registration/management | High |
| 8.3 | Implement claim submission API | High |
| 8.4 | Build claim validation logic | High |
| 8.5 | Create settlement processing | High |
| 8.6 | Implement provider verification (USSD) | Medium |
| 8.7 | Build provider portal API | Medium |
| 8.8 | Add stabilization fund processing | Medium |
| 8.9 | Implement fatal accident payout | Medium |

### Phase 9: Admin Dashboard

| Task | Description | Priority |
|------|-------------|----------|
| 9.1 | Create Admin Service scaffold | Medium |
| 9.2 | Build dashboard statistics API | Medium |
| 9.3 | Implement member management UI | Medium |
| 9.4 | Create incident monitoring dashboard | Medium |
| 9.5 | Build claims review interface | Medium |
| 9.6 | Implement provider management UI | Medium |
| 9.7 | Add reporting/analytics | Medium |
| 9.8 | Build audit log viewer | Low |
| 9.9 | Create system configuration UI | Low |

### Phase 10: Security, Testing & Deployment

| Task | Description | Priority |
|------|-------------|----------|
| 10.1 | Implement AES-256 encryption for sensitive data | Critical |
| 10.2 | Set up TLS 1.3 across all services | Critical |
| 10.3 | Implement rate limiting | High |
| 10.4 | Add input validation/sanitization | High |
| 10.5 | Write unit tests (>80% coverage) | High |
| 10.6 | Write integration tests | High |
| 10.7 | Perform security audit | Critical |
| 10.8 | Load testing (concurrent emergencies) | High |
| 10.9 | Set up production environment | High |
| 10.10 | Configure disaster recovery | Medium |
| 10.11 | Create deployment documentation | Medium |
| 10.12 | IPEC compliance review | High |

---

## 12. MVP Recommendation

For a **6-month pilot with 2,500 members**, the following MVP scope is recommended:

### Must Have (MVP)

| Feature | Justification |
|---------|---------------|
| Member registration (WhatsApp + Agent) | Core user acquisition |
| Basic subscription (Lifeline tier) | Lowest barrier to entry |
| Emergency activation (NFC/QR → WhatsApp) | Core value proposition |
| Payment token generation & verification | Solves the payment problem |
| Basic EMR (blood type, allergies, conditions) | Critical medical info |
| NOK notifications | Family peace of mind |
| EcoCash payment integration | 85%+ market coverage |
| 1-2 ambulance provider integrations | Service delivery |
| Basic admin dashboard | Operations management |

### Nice to Have (Post-MVP)

| Feature | Phase |
|---------|-------|
| Guardian & Shield Plus tiers | Post-pilot |
| Air ambulance support | Post-pilot |
| Full EMR with documents | Post-pilot |
| USSD registration | Post-pilot |
| Multiple payment providers | Post-pilot |
| Counselling booking | Post-pilot |
| Advanced analytics | Post-pilot |

### MVP Success Metrics

| Metric | Target |
|--------|--------|
| Registered members | 2,500 |
| Active subscriptions | 2,000 (80% retention) |
| Emergency activations | Track all |
| Average response time | < 60 seconds |
| Provider settlement time | < 72 hours |
| System uptime | 99.9% |

---

## 13. Technical Stack

### Recommended Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend Framework** | Node.js/NestJS or Python/FastAPI | Strong ecosystem, async support |
| **Database** | PostgreSQL | ACID compliance, JSON support |
| **Cache** | Redis | Session management, rate limiting |
| **Message Queue** | RabbitMQ or AWS SQS | Async processing, reliability |
| **Cloud Provider** | AWS or Azure | Enterprise features, Africa regions |
| **API Gateway** | Kong or AWS API Gateway | Rate limiting, auth, routing |
| **WhatsApp** | 360dialog or Twilio | Business API access |
| **Mobile Money** | Direct EcoCash/Innbucks + Paynow | Local payment coverage |
| **SMS** | Africa's Talking | Regional coverage, reliability |
| **Monitoring** | Prometheus + Grafana | Real-time metrics |
| **Logging** | ELK Stack or CloudWatch | Centralized logging |
| **Container Orchestration** | Kubernetes or ECS | Scalability |

### Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Encryption at rest | AES-256 |
| Encryption in transit | TLS 1.3 |
| Key management | AWS KMS / Azure Key Vault |
| Authentication | JWT with refresh tokens |
| Authorization | RBAC with tiered access |
| Audit logging | All EMR access logged |
| Compliance | HIPAA-aligned, IPEC |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Golden Hour** | First 60 minutes after trauma when medical intervention is most effective |
| **GPT** | Guaranteed Payment Token - digital code guaranteeing provider payment |
| **EMR** | Electronic Medical Record |
| **NOK** | Next of Kin |
| **SACCO** | Savings and Credit Cooperative Organization |
| **IPEC** | Insurance and Pensions Commission (Zimbabwe regulator) |
| **NFC** | Near Field Communication |
| **EcoCash** | Zimbabwe's largest mobile money platform |
| **Innbucks** | Growing mobile money platform in Zimbabwe |

---

## Appendix B: Questions for Stakeholders

Before implementation, clarification is needed on:

1. **Tech stack preference**: Node.js/NestJS, Python/FastAPI, or another preference?
2. **Cloud provider**: AWS or Azure?
3. **MVP scope**: Start with Lifeline tier only, or all three tiers?
4. **WhatsApp API**: Do you have Business API access, or need to plan for approval?
5. **Ambulance providers**: Any specific providers already in discussion?
6. **Insurance partner**: Status of MOU with micro-insurer?
7. **Regulatory**: IPEC approval timeline?

---

**Document Version:** 1.0
**Last Updated:** December 2025
**Status:** Ready for Review
